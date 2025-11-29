from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from ..models import ServiceProvider, AuthorizedPerson, ServiceRequest
from .auth_views import is_authorized_person

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff or is_authorized_person(u))
def admin_dashboard(request):
    """Admin dashboard for authorized persons"""
    # Stats
    total_users = User.objects.count()
    total_providers = ServiceProvider.objects.count()
    pending_providers = ServiceProvider.objects.filter(is_verified=False).count()
    total_requests = ServiceRequest.objects.count()
    
    context = {
        'total_users': total_users,
        'total_providers': total_providers,
        'pending_providers': pending_providers,
        'total_requests': total_requests,
    }
    return render(request, 'solar/admin_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff or is_authorized_person(u))
def admin_users(request):
    """Admin: List all users"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'solar/admin_users.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff or is_authorized_person(u))
def admin_user_detail(request, user_id):
    """Admin: User detail"""
    user = get_object_or_404(User, id=user_id)
    return render(request, 'solar/admin_user_detail.html', {'target_user': user})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff or is_authorized_person(u))
def admin_user_delete(request, user_id):
    """Admin: Delete user"""
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('admin_users')
    return render(request, 'solar/confirm_delete.html', {'object': user})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff or is_authorized_person(u))
def admin_providers(request):
    """Admin: List all service providers"""
    providers = ServiceProvider.objects.all().order_by('-created_at')
    return render(request, 'solar/admin_providers.html', {'providers': providers})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff or is_authorized_person(u))
def admin_provider_detail(request, provider_id):
    """Admin: Service provider detail"""
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    return render(request, 'solar/admin_provider_detail.html', {'provider': provider})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff or is_authorized_person(u))
def admin_provider_approve(request, provider_id):
    """Admin: Approve service provider"""
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    provider.is_verified = True
    provider.save()
    messages.success(request, f'Provider {provider.company_name} approved.')
    return redirect('admin_providers')

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff or is_authorized_person(u))
def admin_provider_delete(request, provider_id):
    """Admin: Delete service provider"""
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    if request.method == 'POST':
        provider.user.delete() # Delete the associated user account too
        messages.success(request, 'Provider deleted successfully.')
        return redirect('admin_providers')
    return render(request, 'solar/confirm_delete.html', {'object': provider})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff or is_authorized_person(u))
def admin_requests(request):
    """Admin: List all service requests"""
    requests = ServiceRequest.objects.all().order_by('-requested_date')
    return render(request, 'solar/admin_requests.html', {'requests': requests})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff or is_authorized_person(u))
def admin_request_detail(request, request_id):
    """Admin: Service request detail"""
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    return render(request, 'solar/admin_request_detail.html', {'service_request': service_request})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff or is_authorized_person(u))
def admin_request_update_status(request, request_id):
    """Admin: Update service request status"""
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status:
            service_request.status = status
            service_request.save()
            messages.success(request, 'Status updated.')
    return redirect('admin_request_detail', request_id=request_id)
