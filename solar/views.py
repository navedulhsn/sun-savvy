from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from decimal import Decimal
import json
import uuid
import secrets
import os

from .models import (
    UserProfile, ServiceProvider, AuthorizedPerson, SolarEstimation, 
    Appliance, FaultDetection, ServiceRequest
)
from .forms import (
    UserRegistrationForm, ServiceProviderRegistrationForm, AuthorizedPersonRegistrationForm,
    SolarEstimationForm, ServiceRequestForm, FaultDetectionForm
)
from .utils import (
    get_solar_irradiance, calculate_solar_potential,
    calculate_panels_needed, calculate_financial_analysis,
    detect_fault_ai, get_panel_types, calculate_panel_capacity_options,
    calculate_appliance_consumption, calculate_savings_roi
)


def is_authorized_person(user):
    """Check if user is an authorized person"""
    return hasattr(user, 'authorizedperson') and user.is_active


def home(request):
    """Home page"""
    return render(request, 'solar/home.html')


def register_selection(request):
    """Role selection page for registration"""
    return render(request, 'solar/register.html')


def register_user(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True  # Temporarily disabled email verification
            user.save()
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                email_verified=True,  # Temporarily disabled
                verification_token=''
            )
            
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'solar/register_user.html', {'form': form})


def register_service_provider(request):
    """Service provider registration"""
    if request.method == 'POST':
        form = ServiceProviderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True  # Temporarily disabled email verification
            user.save()
            
            ServiceProvider.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                zip_code=form.cleaned_data['zip_code'],
                services_offered=form.cleaned_data['services_offered'],
                email_verified=True,  # Temporarily disabled
                verification_token=''
            )
            
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('login')
    else:
        form = ServiceProviderRegistrationForm()
    return render(request, 'solar/register_service_provider.html', {'form': form})


def register_authorized_person(request):
    """Authorized person registration"""
    if request.method == 'POST':
        form = AuthorizedPersonRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            AuthorizedPerson.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                designation=form.cleaned_data['designation'],
                email_verified=True,  # Temporarily disabled
                verification_token=''
            )
            
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('login')
    else:
        form = AuthorizedPersonRegistrationForm()
    return render(request, 'solar/register_authorized_person.html', {'form': form})


def login_view(request):
    """Combined login for all user types with role validation"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('user_type', 'user')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_active:
            # Validate user matches selected role
            is_authorized = is_authorized_person(user)
            is_provider = hasattr(user, 'serviceprovider')
            is_regular_user = hasattr(user, 'userprofile')
            
            role_matched = False
            
            if selected_role == 'authorized_user' and is_authorized:
                role_matched = True
            elif selected_role == 'service_provider' and is_provider:
                role_matched = True
            elif selected_role == 'user' and is_regular_user and not is_authorized and not is_provider:
                role_matched = True
            
            if not role_matched:
                role_names = {
                    'user': 'User',
                    'service_provider': 'Service Provider',
                    'authorized_user': 'Authorized User'
                }
                messages.error(request, f'Invalid role selection. This account is not registered as a {role_names.get(selected_role, selected_role)}. Please select the correct role.')
                return render(request, 'solar/login.html')
            
            login(request, user)
            
            # Redirect based on actual user type
            if is_authorized:
                return redirect('admin_dashboard')
            elif is_provider:
                return redirect('provider_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'solar/login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('login')


def verify_email(request, token):
    """Email verification"""
    try:
        profile = UserProfile.objects.get(verification_token=token)
        profile.email_verified = True
        profile.user.is_active = True
        profile.user.save()
        profile.save()
        messages.success(request, 'Email verified successfully!')
    except UserProfile.DoesNotExist:
        try:
            provider = ServiceProvider.objects.get(verification_token=token)
            provider.email_verified = True
            provider.user.is_active = True
            provider.user.save()
            provider.save()
            messages.success(request, 'Email verified successfully!')
        except ServiceProvider.DoesNotExist:
            try:
                authorized = AuthorizedPerson.objects.get(verification_token=token)
                authorized.email_verified = True
                authorized.user.is_active = True
                authorized.user.save()
                authorized.save()
                messages.success(request, 'Email verified successfully!')
            except AuthorizedPerson.DoesNotExist:
                messages.error(request, 'Invalid verification token.')
    
    return redirect('login')


@login_required
def dashboard(request):
    """User dashboard"""
    # Redirect authorized persons to admin dashboard
    if is_authorized_person(request.user):
        return redirect('admin_dashboard')
    
    estimations = SolarEstimation.objects.filter(user=request.user).order_by('-created_at')[:5]
    fault_detections = FaultDetection.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'estimations': estimations,
        'fault_detections': fault_detections,
    }
    return render(request, 'solar/dashboard.html', context)


@login_required
def provider_dashboard(request):
    """Service provider dashboard"""
    if not hasattr(request.user, 'serviceprovider'):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    provider = request.user.serviceprovider
    requests = ServiceRequest.objects.filter(service_provider=provider).order_by('-requested_date')
    
    # Calculate statistics
    total_requests = requests.count()
    pending_requests = requests.filter(status='pending').count()
    in_progress_requests = requests.filter(status='in_progress').count()
    completed_requests = requests.filter(status='completed').count()
    
    context = {
        'provider': provider,
        'requests': requests,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'in_progress_requests': in_progress_requests,
        'completed_requests': completed_requests,
    }
    return render(request, 'solar/provider_dashboard.html', context)


def solar_estimation(request):
    """Multi-module solar estimation - Only for regular users"""
    # Redirect authorized persons to admin dashboard
    if request.user.is_authenticated and is_authorized_person(request.user):
        messages.info(request, 'This feature is for regular users only. You are redirected to the admin dashboard.')
        return redirect('admin_dashboard')
    
    # Get all appliances for selection
    appliances = Appliance.objects.all().order_by('category', 'name')
    
    # Get panel types
    panel_types = get_panel_types()
    
    # Initialize session storage for results (only if not exists)
    # Results persist during the session until user navigates away or clears them
    if 'estimation_results' not in request.session:
        request.session['estimation_results'] = {
            'location': None,
            'energy': None,
            'roof': None,
            'savings_roi': None,
        }
    
    # Get existing results from session
    location_result = request.session['estimation_results'].get('location')
    energy_result = request.session['estimation_results'].get('energy')
    roof_result = request.session['estimation_results'].get('roof')
    savings_roi_result = request.session['estimation_results'].get('savings_roi')
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        # Clear results
        if action == 'clear_location':
            request.session['estimation_results']['location'] = None
            request.session.modified = True
            messages.info(request, 'Location results cleared.')
            return redirect('solar_estimation')
        
        elif action == 'clear_energy':
            request.session['estimation_results']['energy'] = None
            request.session.modified = True
            messages.info(request, 'Energy consumption results cleared.')
            return redirect('solar_estimation')
        
        elif action == 'clear_roof':
            request.session['estimation_results']['roof'] = None
            request.session['estimation_results']['savings_roi'] = None  # Clear ROI if roof is cleared
            request.session.modified = True
            messages.info(request, 'Roof area results cleared.')
            return redirect('solar_estimation')
        
        elif action == 'clear_savings_roi':
            request.session['estimation_results']['savings_roi'] = None
            request.session.modified = True
            messages.info(request, 'Savings & ROI results cleared.')
            return redirect('solar_estimation')
        
        elif action == 'clear_all_results':
            request.session['estimation_results'] = {
                'location': None,
                'energy': None,
                'roof': None,
                'savings_roi': None,
            }
            request.session.modified = True
            messages.info(request, 'All estimation results cleared.')
            return redirect('solar_estimation')
        
        # Module 1: Location-Based Estimation
        elif action == 'calculate_location':
            location_method = request.POST.get('location_method', 'map')
            
            if location_method == 'map':
                latitude = Decimal(str(request.POST.get('selected_lat', request.POST.get('latitude', 0))))
                longitude = Decimal(str(request.POST.get('selected_lng', request.POST.get('longitude', 0))))
            else:
                try:
                    latitude = Decimal(str(request.POST.get('latitude', 0)))
                    longitude = Decimal(str(request.POST.get('longitude', 0)))
                except:
                    latitude = longitude = Decimal('0')
            
            if latitude and longitude:
                irradiance = get_solar_irradiance(float(latitude), float(longitude))
                address = request.POST.get('address', '')
                city = request.POST.get('city', '')
                state = request.POST.get('state', '')
                
                location_result = {
                    'latitude': float(latitude),
                    'longitude': float(longitude),
                    'address': address,
                    'city': city,
                    'state': state,
                    'irradiance': float(irradiance),
                    'irradiance_unit': 'kWh/m²/day',
                }
                # Save to session
                request.session['estimation_results']['location'] = location_result
                request.session.modified = True
                messages.success(request, f'Location calculated! Solar Irradiance: {irradiance} kWh/m²/day')
            else:
                messages.error(request, 'Please provide valid location coordinates.')
        
        # Module 2: Energy Consumption Estimation
        elif action == 'calculate_energy':
            selected_appliances = []
            
            # Get selected appliances from form
            for key, value in request.POST.items():
                if key.startswith('appliance_'):
                    appliance_id = key.replace('appliance_', '')
                    quantity = request.POST.get(f'quantity_{appliance_id}', '1')
                    hours = request.POST.get(f'hours_{appliance_id}', '0')
                    
                    try:
                        selected_appliances.append({
                            'appliance_id': int(appliance_id),
                            'quantity': int(quantity),
                            'hours_per_day': float(hours),
                        })
                    except:
                        continue
            
            if selected_appliances:
                consumption_data = calculate_appliance_consumption(selected_appliances)
                # Convert appliance objects to serializable format
                serializable_data = {
                    'total_monthly_kwh': consumption_data['total_monthly_kwh'],
                    'appliance_details': []
                }
                for detail in consumption_data['appliance_details']:
                    serializable_data['appliance_details'].append({
                        'appliance_name': detail['appliance'].name,
                        'appliance_power': detail['appliance'].power_rating_watts,
                        'quantity': detail['quantity'],
                        'hours_per_day': detail['hours_per_day'],
                        'monthly_kwh': detail['monthly_kwh'],
                    })
                
                energy_result = serializable_data
                # Save to session
                request.session['estimation_results']['energy'] = energy_result
                request.session.modified = True
                messages.success(request, f'Energy consumption calculated! Total: {consumption_data["total_monthly_kwh"]:.2f} kWh/month')
            else:
                messages.error(request, 'Please select at least one appliance.')
        
        # Module 3: Roof Area Estimation
        elif action == 'calculate_roof':
            try:
                rooftop_length = Decimal(str(request.POST.get('rooftop_length', 0)))
                rooftop_width = Decimal(str(request.POST.get('rooftop_width', 0)))
                
                if rooftop_length > 0 and rooftop_width > 0:
                    rooftop_area = rooftop_length * rooftop_width
                    panel_options = calculate_panel_capacity_options(rooftop_area)
                    
                    roof_result = {
                        'rooftop_length': float(rooftop_length),
                        'rooftop_width': float(rooftop_width),
                        'rooftop_area': float(rooftop_area),
                        'panel_options': panel_options,
                    }
                    # Save to session
                    request.session['estimation_results']['roof'] = roof_result
                    request.session.modified = True
                    messages.success(request, f'Roof area calculated! Available area: {rooftop_area:.2f} m²')
                else:
                    messages.error(request, 'Please enter valid roof dimensions.')
            except Exception as e:
                messages.error(request, f'Error calculating roof area: {str(e)}')
        
        # Module 4: Savings & ROI Calculation
        elif action == 'calculate_savings_roi':
            # Check if all required modules are complete
            location_result = request.session['estimation_results'].get('location')
            energy_result = request.session['estimation_results'].get('energy')
            roof_result = request.session['estimation_results'].get('roof')
            
            if not (location_result and energy_result and roof_result):
                messages.error(request, 'Please complete Location, Energy Consumption, and Roof Area modules first.')
            else:
                try:
                    # Get selected panel option (default: 0 = recommended)
                    selected_panel_index = int(request.POST.get('selected_panel_option', 0))
                    
                    # Get custom electricity rate if provided
                    custom_rate = request.POST.get('electricity_rate', '')
                    electricity_rate = Decimal(str(custom_rate)) if custom_rate else None
                    
                    # Calculate Savings & ROI
                    savings_roi_data = calculate_savings_roi(
                        location_result,
                        energy_result,
                        roof_result,
                        selected_panel_index,
                        electricity_rate
                    )
                    
                    if savings_roi_data:
                        # Save to session
                        request.session['estimation_results']['savings_roi'] = savings_roi_data
                        request.session.modified = True
                        messages.success(request, f'Savings & ROI calculated! Payback Period: {savings_roi_data["payback_period_years"]:.1f} years, ROI: {savings_roi_data["roi_percentage"]:.1f}%')
                    else:
                        messages.error(request, 'Error calculating savings and ROI. Please check your inputs.')
                except Exception as e:
                    import traceback
                    messages.error(request, f'Error calculating savings and ROI: {str(e)}')
                    print(f"Error in calculate_savings_roi: {traceback.format_exc()}")
        
        # Refresh results from session after POST
        location_result = request.session['estimation_results'].get('location')
        energy_result = request.session['estimation_results'].get('energy')
        roof_result = request.session['estimation_results'].get('roof')
        savings_roi_result = request.session['estimation_results'].get('savings_roi')
    
    form = SolarEstimationForm()
    
    # Check if all modules are complete
    all_complete = location_result and energy_result and roof_result and savings_roi_result
    
    return render(request, 'solar/solar_estimation.html', {
        'form': form,
        'appliances': appliances,
        'panel_types': panel_types,
        'location_result': location_result,
        'energy_result': energy_result,
        'roof_result': roof_result,
        'savings_roi_result': savings_roi_result,
        'all_complete': all_complete,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    })


@login_required
def estimation_history(request):
    """View estimation history - Only for regular users"""
    if is_authorized_person(request.user):
        messages.info(request, 'This feature is for regular users only.')
        return redirect('admin_dashboard')
    
    estimations = SolarEstimation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'solar/estimation_history.html', {'estimations': estimations})


def generate_estimation_report(request):
    """Generate downloadable report with all estimation results"""
    from django.http import HttpResponse
    from datetime import datetime
    
    # Get results from session
    if 'estimation_results' not in request.session:
        messages.error(request, 'No estimation results found. Please complete the estimation first.')
        return redirect('solar_estimation')
    
    results = request.session['estimation_results']
    location_result = results.get('location')
    energy_result = results.get('energy')
    roof_result = results.get('roof')
    savings_roi_result = results.get('savings_roi')
    
    if not (location_result and energy_result and roof_result):
        messages.error(request, 'Please complete Location, Energy Consumption, and Roof Area modules before generating a report.')
        return redirect('solar_estimation')
    
    # Generate HTML report
    report_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Solar Estimation Report - SunSavvy</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                color: #333;
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid #4F46E5;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #4F46E5;
                margin: 0;
            }}
            .section {{
                margin-bottom: 30px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }}
            .section h2 {{
                color: #4F46E5;
                border-bottom: 2px solid #4F46E5;
                padding-bottom: 10px;
            }}
            .result-item {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }}
            .result-label {{
                font-weight: 600;
                color: #666;
            }}
            .result-value {{
                font-weight: 700;
                color: #4F46E5;
            }}
            .panel-option {{
                margin: 15px 0;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            .panel-option.recommended {{
                border-color: #10B981;
                background-color: #F0FDF4;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #4F46E5;
                color: white;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #ddd;
                text-align: center;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Solar Energy Estimation Report</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="section">
            <h2>Module 1: Location-Based Estimation</h2>
            <div class="result-item">
                <span class="result-label">Address:</span>
                <span class="result-value">{location_result.get('address', 'N/A')}</span>
            </div>
            <div class="result-item">
                <span class="result-label">City, State:</span>
                <span class="result-value">{location_result.get('city', 'N/A')}, {location_result.get('state', 'N/A')}</span>
            </div>
            <div class="result-item">
                <span class="result-label">Coordinates:</span>
                <span class="result-value">{location_result.get('latitude', 0)}, {location_result.get('longitude', 0)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">Solar Irradiance:</span>
                <span class="result-value">{location_result.get('irradiance', 0)} {location_result.get('irradiance_unit', 'kWh/m²/day')}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>Module 2: Energy Consumption Estimation</h2>
            <div class="result-item">
                <span class="result-label">Total Monthly Consumption:</span>
                <span class="result-value">{energy_result.get('total_monthly_kwh', 0):.2f} kWh/month</span>
            </div>
            <div class="result-item">
                <span class="result-label">Annual Consumption:</span>
                <span class="result-value">{energy_result.get('total_monthly_kwh', 0) * 12:.2f} kWh/year</span>
            </div>
            <h3 style="margin-top: 20px;">Appliance Breakdown:</h3>
            <table>
                <thead>
                    <tr>
                        <th>Appliance</th>
                        <th>Power (W)</th>
                        <th>Quantity</th>
                        <th>Hours/Day</th>
                        <th>Monthly Consumption (kWh)</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for detail in energy_result.get('appliance_details', []):
        report_html += f"""
                    <tr>
                        <td>{detail.get('appliance_name', 'N/A')}</td>
                        <td>{detail.get('appliance_power', 0)}</td>
                        <td>{detail.get('quantity', 0)}</td>
                        <td>{detail.get('hours_per_day', 0):.1f}</td>
                        <td>{detail.get('monthly_kwh', 0):.2f}</td>
                    </tr>
        """
    
    report_html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Module 3: Roof Area Estimation</h2>
            <div class="result-item">
                <span class="result-label">Rooftop Dimensions:</span>
                <span class="result-value">{roof_result.get('rooftop_length', 0)}m × {roof_result.get('rooftop_width', 0)}m</span>
            </div>
            <div class="result-item">
                <span class="result-label">Total Rooftop Area:</span>
                <span class="result-value">{roof_result.get('rooftop_area', 0):.2f} m²</span>
            </div>
            <h3 style="margin-top: 20px;">Available Panel Options:</h3>
    """
    
    for idx, option in enumerate(roof_result.get('panel_options', [])):
        recommended_class = 'recommended' if idx == 0 else ''
        report_html += f"""
            <div class="panel-option {recommended_class}">
                <h4>{option.get('panel_type', 'N/A')} {'(Recommended)' if idx == 0 else ''}</h4>
                <div class="result-item">
                    <span class="result-label">Maximum Panels:</span>
                    <span class="result-value">{option.get('max_panels', 0)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Total Capacity:</span>
                    <span class="result-value">{option.get('total_capacity_kw', 0):.2f} kW</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Area Utilization:</span>
                    <span class="result-value">{option.get('area_utilization', 0):.1f}%</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Estimated Cost:</span>
                    <span class="result-value">${option.get('total_cost', 0):,.0f}</span>
                </div>
            </div>
        """
    
    report_html += f"""
        </div>
    """
    
    # Module 4: Savings & ROI Calculation
    if savings_roi_result:
        report_html += f"""
        <div class="section" style="background-color: #F0FDF4; border: 2px solid #10B981;">
            <h2 style="color: #10B981;">Module 4: Savings & ROI Calculation</h2>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
                <div>
                    <h3 style="color: #4F46E5; margin-bottom: 15px;">Cost Breakdown</h3>
                    <div class="result-item">
                        <span class="result-label">Panel Cost:</span>
                        <span class="result-value">${savings_roi_result.get('panel_cost', 0):,.2f}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Installation Cost:</span>
                        <span class="result-value">${savings_roi_result.get('installation_cost', 0):,.2f}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Inverter Cost:</span>
                        <span class="result-value">${savings_roi_result.get('inverter_cost', 0):,.2f}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Wiring & Mounting:</span>
                        <span class="result-value">${savings_roi_result.get('wiring_mounting_cost', 0):,.2f}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Permits & Inspection:</span>
                        <span class="result-value">${savings_roi_result.get('permits_inspection_cost', 0):,.2f}</span>
                    </div>
                    <div class="result-item" style="border-top: 2px solid #4F46E5; padding-top: 10px; margin-top: 10px;">
                        <span class="result-label" style="font-weight: 700; font-size: 1.1em;">Total Installation Cost:</span>
                        <span class="result-value" style="font-weight: 700; font-size: 1.2em; color: #4F46E5;">${savings_roi_result.get('total_installation_cost', 0):,.2f}</span>
                    </div>
                </div>
                
                <div>
                    <h3 style="color: #10B981; margin-bottom: 15px;">Savings & Returns</h3>
                    <div class="result-item">
                        <span class="result-label">System Capacity:</span>
                        <span class="result-value">{savings_roi_result.get('system_capacity_kw', 0):.2f} kW</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Panels Needed:</span>
                        <span class="result-value">{savings_roi_result.get('panels_needed', 0)}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Monthly Savings:</span>
                        <span class="result-value">${savings_roi_result.get('monthly_savings', 0):,.2f}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Annual Savings:</span>
                        <span class="result-value">${savings_roi_result.get('annual_savings', 0):,.2f}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Payback Period:</span>
                        <span class="result-value">{savings_roi_result.get('payback_period_years', 0):.1f} years</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Total Savings (25 years):</span>
                        <span class="result-value">${savings_roi_result.get('total_savings_over_lifetime', 0):,.2f}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Net Profit:</span>
                        <span class="result-value">${savings_roi_result.get('net_profit', 0):,.2f}</span>
                    </div>
                    <div class="result-item" style="border-top: 2px solid #10B981; padding-top: 10px; margin-top: 10px;">
                        <span class="result-label" style="font-weight: 700; font-size: 1.1em;">ROI Percentage:</span>
                        <span class="result-value" style="font-weight: 700; font-size: 1.2em; color: #10B981;">{savings_roi_result.get('roi_percentage', 0):.1f}%</span>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background-color: #EEF2FF; border-radius: 5px;">
                <strong>Financial Formulas:</strong><br>
                ROI = (Net Profit ÷ Total Installation Cost) × 100<br>
                Payback Period = Total Installation Cost ÷ Annual Savings
            </div>
        </div>
        """
    else:
        report_html += """
        <div class="section" style="background-color: #FEF3C7; border: 2px solid #F59E0B;">
            <h2 style="color: #F59E0B;">Module 4: Savings & ROI Calculation</h2>
            <p style="color: #92400E;">Savings & ROI calculation not completed. Please complete this module for full financial analysis.</p>
        </div>
        """
    
    report_html += f"""
        
        <div class="footer">
            <p>Report generated by SunSavvy Solar Estimation System</p>
            <p>This is an estimate. Please consult with a professional solar installer for accurate assessments.</p>
        </div>
    </body>
    </html>
    """
    
    # Create HTTP response
    response = HttpResponse(report_html, content_type='text/html')
    filename = f'solar_estimation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def service_providers(request):
    """List all service providers"""
    if request.user.is_authenticated and is_authorized_person(request.user):
        messages.info(request, 'This feature is for regular users only.')
        return redirect('admin_dashboard')
    
    providers = ServiceProvider.objects.filter(is_verified=True)
    return render(request, 'solar/service_providers.html', {'providers': providers})


def service_provider_detail(request, provider_id):
    """Service provider detail page"""
    if request.user.is_authenticated and is_authorized_person(request.user):
        messages.info(request, 'This feature is for regular users only.')
        return redirect('admin_dashboard')
    
    provider = get_object_or_404(ServiceProvider, id=provider_id, is_verified=True)
    
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to request a service.')
                return redirect('login')
            
            ServiceRequest.objects.create(
                user=request.user,
                service_provider=provider,
                service_type=form.cleaned_data['service_type'],
                description=form.cleaned_data['description'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
            )
            messages.success(request, 'Service request submitted successfully!')
            return redirect('my_requests')
    else:
        form = ServiceRequestForm()
    
    return render(request, 'solar/service_provider_detail.html', {
        'provider': provider,
        'form': form,
    })


@login_required
def my_requests(request):
    """User's service requests"""
    if is_authorized_person(request.user):
        messages.info(request, 'This feature is for regular users only.')
        return redirect('admin_dashboard')
    
    requests = ServiceRequest.objects.filter(user=request.user).order_by('-requested_date')
    return render(request, 'solar/my_requests.html', {'requests': requests})


def fault_detection(request):
    """AI fault detection - Available to all users"""
    if request.user.is_authenticated and is_authorized_person(request.user):
        messages.info(request, 'This feature is for regular users only.')
        return redirect('admin_dashboard')
    
    detection_result = None
    fault_detection_obj = None
    
    if request.method == 'POST':
        form = FaultDetectionForm(request.POST, request.FILES)
        if form.is_valid():
            fault_detection_obj = form.save(commit=False)
            if request.user.is_authenticated:
                fault_detection_obj.user = request.user
            
            # Save image first
            fault_detection_obj.save()
            
            # Run AI detection
            image_path = fault_detection_obj.image.path
            result = detect_fault_ai(image_path)
            
            fault_detection_obj.fault_type = result['fault_type']
            fault_detection_obj.confidence_score = Decimal(str(result['confidence_score']))
            fault_detection_obj.description = result['description']
            fault_detection_obj.detection_result = result
            fault_detection_obj.save()
            
            detection_result = {
                'fault_type': result['fault_type'],
                'confidence_score': float(result['confidence_score']),
                'description': result['description'],
                'recommendations': result.get('recommendations', 'Regular maintenance recommended.'),
                'image_url': fault_detection_obj.image.url,
                'detection_id': fault_detection_obj.id,
            }
            
            messages.success(request, f'Fault detection complete: {result["fault_type"]}')
    else:
        form = FaultDetectionForm()
    
    # Get service providers for referrals (if fault detected)
    service_providers = None
    if detection_result and detection_result['fault_type'] != 'Normal':
        service_providers = ServiceProvider.objects.filter(is_verified=True)[:3]
    
    return render(request, 'solar/fault_detection.html', {
        'form': form,
        'detection_result': detection_result,
        'service_providers': service_providers,
    })


@login_required
def fault_detection_history(request):
    """Fault detection history"""
    if request.user.is_authenticated and is_authorized_person(request.user):
        messages.info(request, 'This feature is for regular users only.')
        return redirect('admin_dashboard')
    
    detections = FaultDetection.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'solar/fault_detection_history.html', {'detections': detections})


@require_http_methods(["POST"])
def chatbot(request):
    """AI chatbot endpoint"""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    message = data.get('message', '')
    
    # Simple rule-based responses (can be upgraded to OpenAI API)
    responses = {
        'hello': 'Hello! How can I help you with solar energy today?',
        'solar': 'Solar energy is a renewable source that converts sunlight into electricity using solar panels.',
        'cost': 'Solar panel costs vary, but typically range from $0.50 to $1.00 per watt installed.',
        'roi': 'ROI for solar panels typically ranges from 10-25% over 25 years, with payback periods of 5-10 years.',
    }
    
    message_lower = message.lower()
    response = 'I can help you with solar energy questions. Ask me about solar panels, costs, ROI, or installation.'
    
    for key, value in responses.items():
        if key in message_lower:
            response = value
            break
    
    return JsonResponse({'response': response})


# Admin Dashboard Views
@login_required
def admin_dashboard(request):
    """Admin dashboard for authorized persons"""
    if not is_authorized_person(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    total_users = UserProfile.objects.count()
    total_providers = ServiceProvider.objects.count()
    total_requests = ServiceRequest.objects.count()
    pending_requests = ServiceRequest.objects.filter(status='pending').count()
    
    recent_requests = ServiceRequest.objects.order_by('-requested_date')[:5]
    
    context = {
        'total_users': total_users,
        'total_providers': total_providers,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'recent_requests': recent_requests,
    }
    return render(request, 'solar/admin_dashboard.html', context)


@login_required
def admin_users(request):
    """Admin: List all users"""
    if not is_authorized_person(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    user_profiles = UserProfile.objects.filter(user__isnull=False).select_related('user').order_by('-created_at')
    return render(request, 'solar/admin_users.html', {'users': user_profiles})


@login_required
def admin_user_detail(request, user_id):
    """Admin: User detail"""
    if not is_authorized_person(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)
    estimations = SolarEstimation.objects.filter(user=user).order_by('-created_at')
    
    return render(request, 'solar/admin_user_detail.html', {
        'user': user,
        'profile': profile,
        'estimations': estimations,
    })


@login_required
def admin_user_delete(request, user_id):
    """Admin: Delete user"""
    if not is_authorized_person(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            username = user.username
            user.delete()
            messages.success(request, f'User {username} has been deleted successfully.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    
    return redirect('admin_users')


@login_required
def admin_providers(request):
    """Admin: List all service providers"""
    if not is_authorized_person(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    providers = ServiceProvider.objects.all().order_by('-created_at')
    return render(request, 'solar/admin_providers.html', {'providers': providers})


@login_required
def admin_provider_detail(request, provider_id):
    """Admin: Service provider detail"""
    if not is_authorized_person(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    requests = ServiceRequest.objects.filter(service_provider=provider).order_by('-requested_date')
    
    return render(request, 'solar/admin_provider_detail.html', {
        'provider': provider,
        'requests': requests,
    })


@login_required
def admin_provider_approve(request, provider_id):
    """Admin: Approve service provider"""
    if not is_authorized_person(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    provider.is_verified = True
    provider.save()
    messages.success(request, f'{provider.company_name} has been approved.')
    
    return redirect('admin_provider_detail', provider_id=provider_id)


@login_required
def admin_provider_delete(request, provider_id):
    """Admin: Delete service provider"""
    if not is_authorized_person(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            provider = ServiceProvider.objects.get(id=provider_id)
            company_name = provider.company_name
            provider.delete()
            messages.success(request, f'Service provider {company_name} has been deleted successfully.')
        except ServiceProvider.DoesNotExist:
            messages.error(request, 'Service provider not found.')
    
    return redirect('admin_providers')


@login_required
def admin_requests(request):
    """Admin: List all service requests"""
    if not is_authorized_person(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    requests = ServiceRequest.objects.all().order_by('-requested_date')
    return render(request, 'solar/admin_requests.html', {'requests': requests})


@login_required
def admin_request_detail(request, request_id):
    """Admin: Service request detail"""
    if not is_authorized_person(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    return render(request, 'solar/admin_request_detail.html', {
        'service_request': service_request,
    })


@login_required
def admin_request_update_status(request, request_id):
    """Admin: Update service request status"""
    if not is_authorized_person(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ServiceRequest.STATUS_CHOICES):
            service_request.status = new_status
            service_request.save()
            messages.success(request, 'Request status updated successfully.')
        else:
            messages.error(request, 'Invalid status.')
    
    return redirect('admin_request_detail', request_id=request_id)
