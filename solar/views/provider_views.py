from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from ..models import ServiceProvider, ServiceRequest, ProviderPanel
from ..forms import ServiceProviderProfileForm, ProviderPanelForm

@login_required
def provider_dashboard(request):
    """Comprehensive service provider dashboard"""
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Service provider profile not found.')
        return redirect('home')
    
    # Calculate profile completion
    profile_completion = provider.calculate_profile_completion()
    provider.save()
    
    # Get all requests
    all_requests = ServiceRequest.objects.filter(service_provider=provider).order_by('-requested_date')
    
    # Categorize requests
    pending_requests = all_requests.filter(status='pending')
    in_progress_requests = all_requests.filter(status='in_progress')
    completed_requests = all_requests.filter(status='completed')
    quote_requests = all_requests.filter(status='pending')  # Treat pending as quote requests
    
    # Recent activity (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_requests = all_requests.filter(requested_date__gte=seven_days_ago)
    
    # Statistics
    total_requests = all_requests.count()
    total_pending = pending_requests.count()
    total_completed = completed_requests.count()
    
    # Calculate completion rate
    completion_rate = int((total_completed / total_requests * 100)) if total_requests > 0 else 0
    
    context = {
        'provider': provider,
        'profile_completion': profile_completion,
        'all_requests': all_requests[:10],  # Latest 10
        'pending_requests': pending_requests[:5],
        'in_progress_requests': in_progress_requests[:5],
        'completed_requests': completed_requests[:5],
        'quote_requests': quote_requests[:5],
        'recent_activity': recent_requests[:10],
        'total_requests': total_requests,
        'total_pending': total_pending,
        'total_completed': total_completed,
        'completion_rate': completion_rate,
    }
    
    return render(request, 'solar/provider_dashboard.html', context)


@login_required
def provider_profile_edit(request):
    """Edit provider profile"""
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Service provider profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ServiceProviderProfileForm(request.POST, request.FILES, instance=provider)
        if form.is_valid():
            provider = form.save()
            provider.calculate_profile_completion()
            provider.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('provider_dashboard')
    else:
        form = ServiceProviderProfileForm(instance=provider)
    
    return render(request, 'solar/provider_profile_edit.html', {'form': form, 'provider': provider})


@login_required
def provider_requests(request):
    """View all service requests"""
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Service provider profile not found.')
        return redirect('home')
    
    # Filter requests
    status_filter = request.GET.get('status', 'all')
    
    requests_query = ServiceRequest.objects.filter(service_provider=provider).order_by('-requested_date')
    
    if status_filter != 'all':
        requests_query = requests_query.filter(status=status_filter)
    
    context = {
        'provider': provider,
        'requests': requests_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'solar/provider_requests.html', context)


@login_required
def provider_request_detail(request, request_id):
    """View and manage individual service request"""
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Service provider profile not found.')
        return redirect('home')
    
    service_request = get_object_or_404(ServiceRequest, id=request_id, service_provider=provider)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accept':
            service_request.status = 'accepted'
            service_request.save()
            messages.success(request, 'Request accepted.')
        elif action == 'start':
            service_request.status = 'in_progress'
            service_request.save()
            messages.success(request, 'Request marked as in progress.')
        elif action == 'complete':
            service_request.status = 'completed'
            service_request.save()
            messages.success(request, 'Request marked as completed.')
        elif action == 'reject':
            service_request.status = 'cancelled'
            service_request.save()
            messages.success(request, 'Request cancelled.')
        elif action == 'add_note':
            note = request.POST.get('note', '')
            if note:
                # You can add a notes field to ServiceRequest model later
                messages.success(request, 'Note added successfully.')
        
        return redirect('provider_request_detail', request_id=request_id)
    
    context = {
        'provider': provider,
        'service_request': service_request,
    }
    
    return render(request, 'solar/provider_request_detail.html', context)


@login_required
def provider_services(request):
    """Manage services offered"""
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Service provider profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        services = request.POST.get('services_offered', '')
        provider.services_offered = services
        provider.save()
        messages.success(request, 'Services updated successfully!')
        return redirect('provider_dashboard')
    
    context = {
        'provider': provider,
    }
    
    return render(request, 'solar/provider_services.html', context)


@login_required
def provider_panels(request):
    """List all panels for the provider"""
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Service provider profile not found.')
        return redirect('home')
    
    panels = ProviderPanel.objects.filter(provider=provider).order_by('-created_at')
    
    context = {
        'provider': provider,
        'panels': panels,
    }
    
    return render(request, 'solar/provider_panels.html', context)


@login_required
def provider_panel_add(request):
    """Add a new panel to the catalog - panel type is required"""
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Service provider profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProviderPanelForm(request.POST, request.FILES)
        if form.is_valid():
            panel = form.save(commit=False)
            panel.provider = provider
            # Use panel type name if custom name not provided
            if not panel.name:
                panel.name = panel.get_panel_type_display()
            panel.save()
            messages.success(request, f'Panel "{panel.name}" added successfully!')
            return redirect('provider_panels')
    else:
        form = ProviderPanelForm()
    
    context = {
        'provider': provider,
        'form': form,
    }
    
    return render(request, 'solar/provider_panel_form.html', context)


@login_required
def provider_panel_edit(request, panel_id):
    """Edit an existing panel"""
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Service provider profile not found.')
        return redirect('home')
    
    panel = get_object_or_404(ProviderPanel, id=panel_id, provider=provider)
    
    if request.method == 'POST':
        form = ProviderPanelForm(request.POST, request.FILES, instance=panel)
        if form.is_valid():
            form.save()
            messages.success(request, f'Panel "{panel.name}" updated successfully!')
            return redirect('provider_panels')
    else:
        form = ProviderPanelForm(instance=panel)
    
    context = {
        'provider': provider,
        'form': form,
        'panel': panel,
    }
    
    return render(request, 'solar/provider_panel_form.html', context)


@login_required
def provider_panel_delete(request, panel_id):
    """Delete a panel"""
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Service provider profile not found.')
        return redirect('home')
    
    panel = get_object_or_404(ProviderPanel, id=panel_id, provider=provider)
    
    if request.method == 'POST':
        panel_name = panel.name
        panel.delete()
        messages.success(request, f'Panel "{panel_name}" deleted successfully!')
        return redirect('provider_panels')
    
    context = {
        'provider': provider,
        'panel': panel,
    }
    
    return render(request, 'solar/provider_panel_delete.html', context)
