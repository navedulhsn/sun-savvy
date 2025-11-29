from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Sum
from django.db import models
from django.http import HttpResponse
from decimal import Decimal
import csv
from django.conf import settings
from django.core.mail import send_mail
from ..models import SolarEstimation, ServiceProvider, ServiceRequest, Appliance, ProviderPanel
from ..utils import (
    get_solar_irradiance, calculate_solar_potential,
    calculate_panels_needed, calculate_financial_analysis,
    get_panel_types, calculate_panel_capacity_options,
    calculate_appliance_consumption, calculate_savings_roi
)

@login_required
def dashboard(request):
    """Enhanced user dashboard with comprehensive statistics"""
    # Get recent estimations
    estimations = SolarEstimation.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get active service requests
    active_requests = ServiceRequest.objects.filter(
        user=request.user, 
        status__in=['pending', 'in_progress']
    ).order_by('-requested_date')[:5]
    
    # Get fault detections
    from ..models import FaultDetection
    fault_detections = FaultDetection.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Calculate statistics
    total_estimations = SolarEstimation.objects.filter(user=request.user).count()
    total_potential_savings = SolarEstimation.objects.filter(user=request.user).aggregate(
        total=models.Sum('annual_savings')
    )['total'] or 0
    active_requests_count = ServiceRequest.objects.filter(
        user=request.user,
        status__in=['pending', 'in_progress']
    ).count()
    total_fault_detections = FaultDetection.objects.filter(user=request.user).count()
    
    context = {
        'estimations': estimations,
        'active_requests': active_requests,
        'fault_detections': fault_detections,
        'total_estimations': total_estimations,
        'total_potential_savings': total_potential_savings,
        'active_requests_count': active_requests_count,
        'total_fault_detections': total_fault_detections,
    }
    return render(request, 'solar/dashboard.html', context)

@login_required
def solar_estimation(request):
    """Modular solar estimation with session-based storage"""
    
    # Initialize session storage
    if 'location_result' not in request.session:
        request.session['location_result'] = None
    if 'energy_result' not in request.session:
        request.session['energy_result'] = None
    if 'roof_result' not in request.session:
        request.session['roof_result'] = None
    if 'savings_roi_result' not in request.session:
        request.session['savings_roi_result'] = None
    
    # Get all appliances for energy module
    appliances = Appliance.objects.all().order_by('category', 'name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Module 1: Location Calculation
        if action == 'calculate_location':
            location_method = request.POST.get('location_method', 'map')
            
            if location_method == 'map':
                latitude = request.POST.get('selected_lat')
                longitude = request.POST.get('selected_lng')
            else:
                latitude = request.POST.get('latitude')
                longitude = request.POST.get('longitude')
            
            address = request.POST.get('address', '')
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            
            if latitude and longitude:
                try:
                    # Get solar irradiance
                    irradiance = get_solar_irradiance(float(latitude), float(longitude))
                    
                    request.session['location_result'] = {
                        'latitude': float(latitude),
                        'longitude': float(longitude),
                        'address': address,
                        'city': city,
                        'state': state,
                        'irradiance': float(irradiance),
                        'irradiance_unit': 'kWh/m²/day'
                    }
                    request.session.modified = True
                    messages.success(request, f'✅ Location analysis complete! Solar irradiance: {irradiance:.2f} kWh/m²/day')
                except Exception as e:
                    messages.error(request, f'Error calculating solar irradiance: {str(e)}')
        
        # Module 2: Energy Consumption Calculation
        elif action == 'calculate_energy':
            try:
                appliance_details = []
                total_monthly_kwh = 0
                
                for appliance in appliances:
                    checkbox_name = f'appliance_{appliance.id}'
                    if request.POST.get(checkbox_name):
                        try:
                            quantity = int(request.POST.get(f'quantity_{appliance.id}', 1))
                            hours_per_day = float(request.POST.get(f'hours_{appliance.id}', 0))
                            
                            if hours_per_day > 0:
                                # Calculate monthly consumption for this appliance
                                daily_kwh = (appliance.power_rating_watts * quantity * hours_per_day) / 1000
                                monthly_kwh = daily_kwh * 30
                                total_monthly_kwh += monthly_kwh
                                
                                appliance_details.append({
                                    'appliance_name': appliance.name,
                                    'quantity': quantity,
                                    'hours_per_day': hours_per_day,
                                    'monthly_kwh': monthly_kwh
                                })
                        except (ValueError, TypeError) as e:
                            messages.warning(request, f'Invalid input for {appliance.name}: {str(e)}')
                            continue
                
                if total_monthly_kwh > 0:
                    request.session['energy_result'] = {
                        'total_monthly_kwh': total_monthly_kwh,
                        'appliance_details': appliance_details
                    }
                    request.session.modified = True
                    messages.success(request, f'✅ Energy consumption calculated: {total_monthly_kwh:.2f} kWh/month')
                else:
                    messages.error(request, 'Please select at least one appliance and set usage hours greater than 0.')
            except Exception as e:
                messages.error(request, f'Error calculating energy consumption: {str(e)}')
        
        # Module 3: Roof Area Calculation
        elif action == 'calculate_roof':
            try:
                rooftop_length = float(request.POST.get('rooftop_length', 0))
                rooftop_width = float(request.POST.get('rooftop_width', 0))
                
                if rooftop_length > 0 and rooftop_width > 0:
                    rooftop_area = rooftop_length * rooftop_width
                    
                    # Calculate panel options
                    panel_options = calculate_panel_capacity_options(rooftop_area)
                    
                    request.session['roof_result'] = {
                        'rooftop_length': rooftop_length,
                        'rooftop_width': rooftop_width,
                        'rooftop_area': rooftop_area,
                        'panel_options': panel_options
                    }
                    request.session.modified = True
                    messages.success(request, f'✅ Roof area calculated: {rooftop_area:.2f} m² with {len(panel_options)} panel options')
                else:
                    messages.error(request, 'Please enter valid roof dimensions (must be greater than 0).')
            except (ValueError, TypeError) as e:
                messages.error(request, f'Invalid roof dimensions: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error calculating roof area: {str(e)}')
        
        # Module 4: Savings & ROI Calculation
        elif action == 'calculate_savings_roi':
            try:
                location_result = request.session.get('location_result')
                energy_result = request.session.get('energy_result')
                roof_result = request.session.get('roof_result')
                
                if not (location_result and energy_result and roof_result):
                    messages.error(request, 'Please complete all previous modules first (Location, Energy, and Roof).')
                else:
                    selected_option_index = int(request.POST.get('selected_panel_option', 0))
                    electricity_rate = request.POST.get('electricity_rate')
                    
                    # Calculate savings and ROI
                    results = calculate_savings_roi(
                        location_result=location_result,
                        energy_result=energy_result,
                        roof_result=roof_result,
                        selected_panel_option_index=selected_option_index,
                        electricity_rate=float(electricity_rate) if electricity_rate else None
                    )
                    
                    if results:
                        request.session['savings_roi_result'] = results
                        request.session.modified = True
                        
                        # Save to database
                        try:
                            estimation = SolarEstimation.objects.create(
                                user=request.user,
                                latitude=Decimal(str(location_result['latitude'])),
                                longitude=Decimal(str(location_result['longitude'])),
                                address=location_result.get('address', ''),
                                city=location_result.get('city', ''),
                                state=location_result.get('state', ''),
                                monthly_consumption_kwh=Decimal(str(energy_result['total_monthly_kwh'])),
                                rooftop_length=Decimal(str(roof_result['rooftop_length'])),
                                rooftop_width=Decimal(str(roof_result['rooftop_width'])),
                                rooftop_area=Decimal(str(roof_result['rooftop_area'])),
                                solar_irradiance=Decimal(str(location_result['irradiance'])),
                                panels_needed=int(results['panels_needed']),
                                panel_capacity_kw=Decimal(str(results['system_capacity_kw'])),
                                estimated_cost=Decimal(str(results['total_installation_cost'])),
                                annual_savings=Decimal(str(results['annual_savings'])),
                                payback_period_years=Decimal(str(results['payback_period_years'])),
                                roi_percentage=Decimal(str(results['roi_percentage'])),
                                annual_energy_generated=Decimal(str(results['annual_energy_generated']))
                            )
                            messages.success(request, f'✅ Complete! System: {results["system_capacity_kw"]:.2f} kW, Annual Savings: PKR {results["annual_savings"]:.0f}, ROI: {results["roi_percentage"]:.1f}%')
                        except Exception as e:
                            messages.warning(request, f'Analysis completed but not saved to database: {str(e)}')
                    else:
                        messages.error(request, 'Unable to calculate savings. Please check your inputs.')
            except Exception as e:
                messages.error(request, f'Error calculating savings: {str(e)}')
        
        # Clear actions
        elif action == 'clear_location':
            request.session['location_result'] = None
            request.session.modified = True
            messages.info(request, 'Location results cleared.')
        
        elif action == 'clear_energy':
            request.session['energy_result'] = None
            request.session.modified = True
            messages.info(request, 'Energy results cleared.')
        
        elif action == 'clear_roof':
            request.session['roof_result'] = None
            request.session.modified = True
            messages.info(request, 'Roof results cleared.')
        
        elif action == 'clear_savings_roi':
            request.session['savings_roi_result'] = None
            request.session.modified = True
            messages.info(request, 'Financial results cleared.')
        
        return redirect('solar_estimation')
    
    # Check if all modules are complete
    all_complete = (
        request.session.get('location_result') and
        request.session.get('energy_result') and
        request.session.get('roof_result') and
        request.session.get('savings_roi_result')
    )
    
    context = {
        'appliances': appliances,
        'location_result': request.session.get('location_result'),
        'energy_result': request.session.get('energy_result'),
        'roof_result': request.session.get('roof_result'),
        'savings_roi_result': request.session.get('savings_roi_result'),
        'all_complete': all_complete,
    }
    
    return render(request, 'solar/solar_estimation.html', context)

@login_required
def estimation_history(request):
    """View estimation history - Only for regular users"""
    estimations = SolarEstimation.objects.filter(user=request.user).order_by('-created_at')
    stats = estimations.aggregate(
        avg_panels=Avg('panels_needed'),
        avg_cost=Avg('estimated_cost'),
        avg_savings=Avg('annual_savings'),
    )
    context = {
        'estimations': estimations,
        'total_estimations': estimations.count(),
        'avg_panels_needed': stats.get('avg_panels') or 0,
        'avg_estimated_cost': stats.get('avg_cost') or 0,
        'avg_annual_savings': stats.get('avg_savings') or 0,
    }
    return render(request, 'solar/estimation_history.html', context)

@login_required
def generate_estimation_report(request):
    """Generate a downloadable CSV report for the latest estimation."""
    try:
        # Prefer the most recent saved estimation
        estimation = SolarEstimation.objects.filter(user=request.user).order_by('-created_at').first()

        # If none saved (e.g., DB save failed), fall back to session data
        if not estimation:
            location_result = request.session.get('location_result')
            energy_result = request.session.get('energy_result')
            roof_result = request.session.get('roof_result')
            savings_roi_result = request.session.get('savings_roi_result')

            if not (location_result and energy_result and roof_result and savings_roi_result):
                messages.error(request, 'No estimation data found to generate report.')
                return redirect('solar_estimation')

            # Prepare a CSV from session data
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="sun_savvy_estimation_report.csv"'
            writer = csv.writer(response)

            writer.writerow(['Section', 'Field', 'Value'])
            writer.writerow(['Location', 'Address', location_result.get('address', '')])
            writer.writerow(['Location', 'City', location_result.get('city', '')])
            writer.writerow(['Location', 'State', location_result.get('state', '')])
            writer.writerow(['Location', 'Latitude', location_result.get('latitude', '')])
            writer.writerow(['Location', 'Longitude', location_result.get('longitude', '')])
            writer.writerow(['Location', 'Solar Irradiance (kWh/m²/day)', location_result.get('irradiance', '')])

            writer.writerow(['Energy', 'Monthly Consumption (kWh)', energy_result.get('total_monthly_kwh', '')])

            writer.writerow(['Roof', 'Length (m)', roof_result.get('rooftop_length', '')])
            writer.writerow(['Roof', 'Width (m)', roof_result.get('rooftop_width', '')])
            writer.writerow(['Roof', 'Area (m²)', roof_result.get('rooftop_area', '')])

            writer.writerow(['Financial', 'Panels Needed', savings_roi_result.get('panels_needed', '')])
            writer.writerow(['Financial', 'System Capacity (kW)', savings_roi_result.get('system_capacity_kw', '')])
            writer.writerow(['Financial', 'Total Cost (PKR)', savings_roi_result.get('total_installation_cost', '')])
            writer.writerow(['Financial', 'Annual Savings (PKR)', savings_roi_result.get('annual_savings', '')])
            writer.writerow(['Financial', 'Payback Period (years)', savings_roi_result.get('payback_period_years', '')])
            writer.writerow(['Financial', 'ROI (%)', savings_roi_result.get('roi_percentage', '')])
            writer.writerow(['Financial', 'Annual Energy Generated (kWh)', savings_roi_result.get('annual_energy_generated', '')])

            return response

        # Build CSV from saved estimation
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sun_savvy_estimation_report.csv"'
        writer = csv.writer(response)

        writer.writerow(['Section', 'Field', 'Value'])
        writer.writerow(['Location', 'Address', estimation.address])
        writer.writerow(['Location', 'City', estimation.city])
        writer.writerow(['Location', 'State', estimation.state])
        writer.writerow(['Location', 'Latitude', estimation.latitude])
        writer.writerow(['Location', 'Longitude', estimation.longitude])
        writer.writerow(['Location', 'Solar Irradiance (kWh/m²/day)', estimation.solar_irradiance])

        writer.writerow(['Energy', 'Monthly Consumption (kWh)', estimation.monthly_consumption_kwh])

        writer.writerow(['Roof', 'Length (m)', estimation.rooftop_length])
        writer.writerow(['Roof', 'Width (m)', estimation.rooftop_width])
        writer.writerow(['Roof', 'Area (m²)', estimation.rooftop_area])

        writer.writerow(['Financial', 'Panels Needed', estimation.panels_needed])
        writer.writerow(['Financial', 'System Capacity (kW)', estimation.panel_capacity_kw])
        writer.writerow(['Financial', 'Total Cost (PKR)', estimation.estimated_cost])
        writer.writerow(['Financial', 'Annual Savings (PKR)', estimation.annual_savings])
        writer.writerow(['Financial', 'Payback Period (years)', estimation.payback_period_years])
        writer.writerow(['Financial', 'ROI (%)', estimation.roi_percentage])
        writer.writerow(['Financial', 'Annual Energy Generated (kWh)', estimation.annual_energy_generated])

        return response
    except Exception as e:
        messages.error(request, f'Failed to generate report: {str(e)}')
        return redirect('solar_estimation')

def service_providers(request):
    """List all service providers"""
    providers = ServiceProvider.objects.filter(is_verified=True)
    return render(request, 'solar/service_providers.html', {'providers': providers})

def service_provider_detail(request, provider_id):
    """Service provider detail page"""
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    
    if request.method == 'POST' and request.user.is_authenticated:
        # Handle service request
        service_type = request.POST.get('service_type')
        description = request.POST.get('description')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        
        sr = ServiceRequest.objects.create(
            user=request.user,
            service_provider=provider,
            service_type=service_type,
            description=description,
            address=address,
            phone=phone
        )
        try:
            subject = 'New Service Request'
            body = f'You have a new service request from {request.user.get_full_name() or request.user.username}:\n' \
                   f'Type: {service_type}\n' \
                   f'Phone: {phone}\n' \
                   f'Address: {address}\n' \
                   f'Request ID: #{sr.id}'
            from_email = getattr(settings, 'EMAIL_HOST_USER', None) or 'no-reply@sunsavvy.local'
            recipient = [provider.email]
            send_mail(subject, body, from_email, recipient, fail_silently=True)
        except Exception:
            pass
        messages.success(request, 'Service request sent successfully!')
        return redirect('my_requests')
    
    # Build provider services list and panel catalog with provider-specific pricing
    services_list = [s.strip() for s in provider.services_offered.split(',')] if provider.services_offered else []
    panel_catalog = []
    # Try loading provider's own product listings (if table/migrations exist)
    try:
        provider_panels = list(ProviderPanel.objects.filter(provider=provider, is_active=True))
    except Exception:
        provider_panels = []
    try:
        # Convert provider USD rates to PKR for display
        usd_to_pkr = Decimal(str(getattr(settings, 'USD_TO_PKR_RATE', '280')))
        price_per_watt = Decimal(str(provider.price_per_watt)) * usd_to_pkr
        install_per_watt = Decimal(str(provider.installation_cost_per_watt)) * usd_to_pkr
    except Exception:
        price_per_watt = Decimal('0')
        install_per_watt = Decimal('0')

    for pt in get_panel_types():
        power_watts = Decimal(str(pt.get('power_watts', 0)))
        hardware_price = (power_watts * price_per_watt) if power_watts else Decimal('0')
        installed_price = (power_watts * (price_per_watt + install_per_watt)) if power_watts else Decimal('0')
        panel_catalog.append({
            'name': pt.get('name', ''),
            'power_watts': pt.get('power_watts'),
            'efficiency': pt.get('efficiency'),
            'area_sqm': pt.get('area_sqm'),
            'hardware_price': hardware_price,
            'installed_price': installed_price,
        })

    context = {
        'provider': provider,
        'services_list': services_list,
        'panel_catalog': panel_catalog,
        'provider_panels': provider_panels,
    }
    return render(request, 'solar/service_provider_detail.html', context)

@login_required
def my_requests(request):
    """User's service requests"""
    requests = ServiceRequest.objects.filter(user=request.user).order_by('-requested_date')
    return render(request, 'solar/my_requests.html', {'requests': requests})
