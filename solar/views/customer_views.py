from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Sum, Q
from django.db import models, connection
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
import csv
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from ..models import SolarEstimation, ServiceProvider, ServiceRequest, Appliance, ProviderPanel, FaultDetection
from ..forms import ServiceRequestForm
from ..utils import (
    get_solar_irradiance, calculate_solar_potential,
    calculate_panels_needed, calculate_financial_analysis,
    get_panel_types, calculate_panel_capacity_options,
    calculate_appliance_consumption, calculate_savings_roi,
    validate_coordinates, validate_pakistan_location,
    geocode_address, reverse_geocode, analyze_location_with_gemini
)

@login_required
def dashboard(request):
    """Enhanced user dashboard with comprehensive statistics"""
    try:
        # Get all estimations with error handling for invalid Decimal values
        # Use values_list to avoid Decimal conversion during query evaluation
        valid_estimations = []
        total_potential_savings = 0
        
        try:
            # Use raw SQL to get IDs first, avoiding Decimal conversion
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM solar_solarestimation 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC
                """, [request.user.id])
                estimation_ids = [row[0] for row in cursor.fetchall()]
            
            # Now load each record individually, catching errors per record
            for est_id in estimation_ids:
                try:
                    est = SolarEstimation.objects.get(id=est_id)
                    # Validate all Decimal fields by accessing them
                    _ = est.latitude
                    _ = est.longitude
                    _ = est.monthly_consumption_kwh
                    _ = est.rooftop_area
                    _ = est.solar_irradiance
                    _ = est.panel_capacity_kw
                    _ = est.estimated_cost
                    _ = est.annual_savings
                    _ = est.payback_period_years
                    _ = est.roi_percentage
                    _ = est.annual_energy_generated
                    valid_estimations.append(est)
                    # Calculate savings safely
                    try:
                        total_potential_savings += float(est.annual_savings)
                    except (InvalidOperation, ValueError, TypeError, AttributeError):
                        pass
                except (InvalidOperation, ValueError, TypeError, AttributeError, SolarEstimation.DoesNotExist):
                    # Skip invalid records
                    continue
        except Exception as e:
            # If query itself fails, try fallback method
            try:
                # Fallback: try using values() to get raw data
                all_estimations = SolarEstimation.objects.filter(user=request.user).values(
                    'id', 'latitude', 'longitude', 'monthly_consumption_kwh', 
                    'rooftop_area', 'solar_irradiance', 'panel_capacity_kw',
                    'estimated_cost', 'annual_savings', 'payback_period_years',
                    'roi_percentage', 'annual_energy_generated', 'panels_needed',
                    'address', 'city', 'state', 'created_at'
                ).order_by('-created_at')
                
                # Convert to model instances manually
                for est_data in all_estimations:
                    try:
                        est = SolarEstimation.objects.get(id=est_data['id'])
                        # Validate by accessing fields
                        _ = est.latitude
                        _ = est.annual_savings
                        valid_estimations.append(est)
                        try:
                            total_potential_savings += float(est.annual_savings)
                        except (InvalidOperation, ValueError, TypeError, AttributeError):
                            pass
                    except (InvalidOperation, ValueError, TypeError, AttributeError, SolarEstimation.DoesNotExist):
                        continue
            except Exception:
                # If all methods fail, just use empty list
                valid_estimations = []
                total_potential_savings = 0
        
        # Get recent valid estimations (limit to 5)
        estimations = valid_estimations[:5]
        
        # Get active service requests
        try:
            active_requests = ServiceRequest.objects.filter(
                user=request.user, 
                status__in=['pending', 'in_progress']
            ).order_by('-requested_date')[:5]
        except Exception:
            active_requests = []
        
        # Get fault detections
        try:
            fault_detections = FaultDetection.objects.filter(user=request.user).order_by('-created_at')[:5]
        except Exception:
            fault_detections = []
        
        # Calculate statistics from valid estimations only
        total_estimations = len(valid_estimations)
        
        # Get counts safely
        try:
            active_requests_count = ServiceRequest.objects.filter(
                user=request.user,
                status__in=['pending', 'in_progress']
            ).count()
        except Exception:
            active_requests_count = 0
        
        try:
            total_fault_detections = FaultDetection.objects.filter(user=request.user).count()
        except Exception:
            total_fault_detections = 0
        
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
    except Exception as e:
        import traceback
        error_msg = f'Error loading dashboard: {str(e)}'
        # Log the full traceback for debugging
        print(f"Dashboard Error: {error_msg}")
        print(traceback.format_exc())
        
        messages.error(request, error_msg)
        # Return minimal context to prevent template errors
        context = {
            'estimations': [],
            'active_requests': [],
            'fault_detections': [],
            'total_estimations': 0,
            'total_potential_savings': 0,
            'active_requests_count': 0,
            'total_fault_detections': 0,
        }
        return render(request, 'solar/dashboard.html', context)

@login_required
def solar_estimation(request):
    """Redirect to first module of multi-page estimation flow"""
    # Handle POST requests (e.g., Clear All button)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'clear_all':
            request.session['location_result'] = None
            request.session['energy_result'] = None
            request.session['roof_result'] = None
            request.session['savings_roi_result'] = None
            request.session.modified = True
            request.session.save()  # Force save
            messages.success(request, 'All estimation data cleared. You can start a new estimation.')
            return redirect('estimation_location')
    
    # Handle "new estimation" parameter - clear all session data
    if request.GET.get('new') == '1':
        request.session['location_result'] = None
        request.session['energy_result'] = None
        request.session['roof_result'] = None
        request.session['savings_roi_result'] = None
        request.session.modified = True
        request.session.save()  # Force save
        messages.info(request, 'Starting a new estimation. All previous data has been cleared.')
    
    # Redirect to first module
    return redirect('estimation_location')

def _initialize_estimation_session(request):
    """Helper function to initialize estimation session variables"""
    if 'location_result' not in request.session:
        request.session['location_result'] = None
    if 'energy_result' not in request.session:
        request.session['energy_result'] = None
    if 'roof_result' not in request.session:
        request.session['roof_result'] = None
    if 'savings_roi_result' not in request.session:
        request.session['savings_roi_result'] = None
    request.session.modified = True

def _get_estimation_progress(request):
    """Helper function to calculate estimation progress"""
    completed_modules = sum([
        1 if request.session.get('location_result') else 0,
        1 if request.session.get('energy_result') else 0,
        1 if request.session.get('roof_result') else 0,
        1 if request.session.get('savings_roi_result') else 0,
    ])
    progress_percentage = (completed_modules / 4) * 100
    return completed_modules, progress_percentage

@login_required
def estimation_location(request):
    """Module 1: Location Based Estimation - Multi-page flow with two input methods"""
    # Initialize session
    _initialize_estimation_session(request)
    
    # Initialize location_result variable (will be set in POST or retrieved from session)
    location_result = None
    
    # Handle "new estimation" parameter
    if request.GET.get('new') == '1':
        request.session['location_result'] = None
        request.session['energy_result'] = None
        request.session['roof_result'] = None
        request.session['savings_roi_result'] = None
        request.session.modified = True
        messages.info(request, 'Starting a new estimation. All previous data has been cleared.')
        return redirect('estimation_location')
    
    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'calculate_location':
            input_method = request.POST.get('input_method', 'address')  # 'address' or 'coordinates'
            
            print(f"DEBUG: Action = {action}, Input method = {input_method}")
            print(f"DEBUG: POST data = {dict(request.POST)}")
            
            latitude = None
            longitude = None
            address = ''
            city = ''
            state = ''
            formatted_address = ''
            
            if input_method == 'address':
                # Location-based input: geocode city/state to get coordinates (address is optional)
                address = request.POST.get('address', '').strip()
                city = request.POST.get('city', '').strip()
                state = request.POST.get('state', '').strip()
                
                print(f"DEBUG: Location input - address={address}, city={city}, state={state}")
                
                # Only city and state are required, address is optional
                if not (city and state):
                    messages.error(request, 'Please provide city and state/province.')
                else:
                    # Geocode location (city, state) - address is optional
                    print("DEBUG: Attempting geocoding...")
                    success, lat, lng, formatted_addr, error_msg = geocode_address(address or city, city, state)
                    print(f"DEBUG: Geocoding result - success={success}, lat={lat}, lng={lng}, error={error_msg}")
                    
                    if success:
                        latitude = lat
                        longitude = lng
                        formatted_address = formatted_addr
                        # Use provided address or formatted address
                        if not address:
                            address = formatted_address
                    else:
                        messages.error(request, f'Could not find location: {error_msg}')
                        print(f"DEBUG: Geocoding failed: {error_msg}")
            
            elif input_method == 'coordinates':
                # Coordinates-based input: validate and use directly
                lat_str = request.POST.get('latitude', '').strip()
                lng_str = request.POST.get('longitude', '').strip()
                
                print(f"DEBUG: Coordinates input - lat={lat_str}, lng={lng_str}")
                
                if not (lat_str and lng_str):
                    messages.error(request, 'Please provide both latitude and longitude.')
                else:
                    # Validate coordinates
                    is_valid, error_msg = validate_coordinates(lat_str, lng_str)
                    
                    if is_valid:
                        latitude = float(lat_str)
                        longitude = float(lng_str)
                        
                        # Reverse geocode to get address
                        rev_success, formatted_addr, rev_city, rev_state, rev_error = reverse_geocode(latitude, longitude)
                        if rev_success:
                            formatted_address = formatted_addr
                            if rev_city:
                                city = rev_city
                            if rev_state:
                                state = rev_state
                            # Get address from form if provided
                            address = request.POST.get('address', '').strip() or formatted_address
                    else:
                        messages.error(request, error_msg)
            
            # If we have valid coordinates, proceed with irradiance calculation
            print(f"DEBUG: Final coordinates - lat={latitude}, lng={longitude}")
            
            if latitude and longitude:
                try:
                    print("DEBUG: Getting solar irradiance...")
                    # Get solar irradiance with multi-source approach (always returns a result, even if random)
                    irradiance_result = get_solar_irradiance(latitude, longitude)
                    print(f"DEBUG: Irradiance result = {irradiance_result}")
                    
                    # Ensure we always have an irradiance value (function should always return one)
                    if not irradiance_result or irradiance_result.get('irradiance') is None:
                        # Last resort: generate random value (4.8 to 5.8 for Pakistan)
                        import random
                        random_irradiance = round(random.uniform(4.8, 5.8), 2)
                        irradiance_result = {
                            'irradiance': Decimal(str(random_irradiance)),
                            'source': 'Random (Pakistan Range)',
                            'confidence': 'low',
                            'error': 'All APIs failed. Using random value for Pakistan.'
                        }
                    
                    # Always get location analysis (has fallback if no API key)
                    gemini_analysis = None
                    try:
                        gemini_analysis = analyze_location_with_gemini(
                            address or formatted_address or f"{city}, {state}",
                            city or '',
                            state or '',
                            latitude,
                            longitude
                        )
                    except Exception as gemini_error:
                        print(f"Location analysis error (non-critical): {gemini_error}")
                        # Create basic fallback analysis
                        gemini_analysis = {
                            'success': True,
                            'location_summary': f"Location in {city or 'Pakistan'} has good solar potential.",
                            'climate_zone': 'Semi-arid',
                            'irradiance_estimate': 5.5,
                            'recommendations': 'Standard solar installation recommended.'
                        }
                    
                    # Convert Decimal to float for session storage
                    irradiance_value = irradiance_result['irradiance']
                    if isinstance(irradiance_value, Decimal):
                        irradiance_value = float(irradiance_value)
                    else:
                        irradiance_value = float(irradiance_value)
                    
                    # Store results in session
                    location_result_data = {
                        'latitude': float(latitude),
                        'longitude': float(longitude),
                        'address': address or formatted_address or f"{city}, {state}",
                        'formatted_address': formatted_address or address or '',
                        'city': city or '',
                        'state': state or '',
                        'irradiance': irradiance_value,
                        'irradiance_unit': 'kWh/m²/day',
                        'irradiance_source': irradiance_result.get('source', 'Unknown'),
                        'irradiance_confidence': irradiance_result.get('confidence', 'low'),
                    }
                    
                    # Always add location analysis (has fallback)
                    if gemini_analysis:
                        location_result_data['gemini_analysis'] = gemini_analysis
                    
                    print(f"DEBUG: Saving to session - {location_result_data}")
                    # Save to session
                    request.session['location_result'] = location_result_data
                    request.session.modified = True
                    request.session.save()  # Force immediate save
                    
                    # Verify session was saved
                    saved_result = request.session.get('location_result')
                    print(f"DEBUG: Session saved - {saved_result}")
                    
                    source_info = f" (Source: {irradiance_result.get('source', 'Unknown')})"
                    messages.success(
                        request,
                        f'✅ Location analysis complete! Solar irradiance: {irradiance_value:.2f} kWh/m²/day{source_info}'
                    )
                    
                    # Don't redirect - continue to bottom to render with results
                    # This ensures results show immediately
                
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"DEBUG: Location calculation error: {error_trace}")
                    # Even on error, try to generate a random result
                    try:
                        import random
                        random_irradiance = round(random.uniform(4.8, 5.8), 2)
                        location_result_data = {
                            'latitude': float(latitude),
                            'longitude': float(longitude),
                            'address': address or formatted_address or f"{city}, {state}",
                            'formatted_address': formatted_address or address or '',
                            'city': city or '',
                            'state': state or '',
                            'irradiance': random_irradiance,
                            'irradiance_unit': 'kWh/m²/day',
                            'irradiance_source': 'Random (Pakistan Range)',
                            'irradiance_confidence': 'low',
                        }
                        request.session['location_result'] = location_result_data
                        request.session.modified = True
                        request.session.save()
                        messages.warning(request, f'API error occurred. Using estimated irradiance: {random_irradiance:.2f} kWh/m²/day')
                        
                        # Don't redirect - continue to bottom to render with results
                    except:
                        messages.error(request, f'Error calculating solar irradiance: {str(e)}')
            else:
                if input_method == 'address':
                    messages.warning(request, 'Could not get coordinates from address. Please try entering coordinates manually.')
                elif input_method == 'coordinates':
                    messages.warning(request, 'Please provide valid coordinates.')
                print(f"DEBUG: No valid coordinates - input_method={input_method}")
    
        elif action == 'clear_location':
            request.session['location_result'] = None
            request.session.modified = True
            request.session.save()  # Force save
            messages.info(request, 'Location results cleared.')
            # Continue to bottom to render
        
        elif action == 'clear_all':
            request.session['location_result'] = None
            request.session['energy_result'] = None
            request.session['roof_result'] = None
            request.session['savings_roi_result'] = None
            request.session.modified = True
            request.session.save()  # Force save
            messages.success(request, 'All estimation data cleared. Starting fresh.')
            return redirect('estimation_location')
    
    # Get progress and all results for navigation
    completed_modules, progress_percentage = _get_estimation_progress(request)
    
    # Get location_result from session (always read from session after redirect)
    location_result = request.session.get('location_result')
    
    # Debug session
    print(f"DEBUG: Final location_result from session = {location_result}")
    print(f"DEBUG: Session keys = {list(request.session.keys())}")
    if location_result:
        print(f"DEBUG: location_result type = {type(location_result)}")
        if isinstance(location_result, dict):
            print(f"DEBUG: location_result keys = {list(location_result.keys())}")
            print(f"DEBUG: location_result.irradiance = {location_result.get('irradiance')}")
        else:
            print(f"DEBUG: location_result is not a dict: {type(location_result)}")
    else:
        print("DEBUG: location_result is None or empty")
    
    energy_result = request.session.get('energy_result')
    roof_result = request.session.get('roof_result')
    savings_roi_result = request.session.get('savings_roi_result')
    
    context = {
        'location_result': location_result,
        'energy_result': energy_result,
        'roof_result': roof_result,
        'savings_roi_result': savings_roi_result,
        'completed_modules': completed_modules,
        'progress_percentage': progress_percentage,
        'current_module': 1,
        'total_modules': 4,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY if settings.GOOGLE_MAPS_API_KEY else None,
        'HAS_GOOGLE_MAPS': bool(settings.GOOGLE_MAPS_API_KEY and settings.GOOGLE_MAPS_API_KEY.strip()),
    }
    
    print(f"DEBUG: Rendering with location_result = {context.get('location_result')}")
    if context.get('location_result'):
        lr = context.get('location_result')
        if isinstance(lr, dict):
            print(f"DEBUG: location_result.irradiance in context = {lr.get('irradiance')}")
            print(f"DEBUG: location_result has {len(lr)} keys: {list(lr.keys())}")
        else:
            print(f"DEBUG: location_result is not a dict in context: {type(lr)}")
    else:
        print("DEBUG: No location_result in context - will show form")
    return render(request, 'solar/estimation_location.html', context)

@login_required
def estimation_energy(request):
    """Module 2: Energy Consumption Estimation - Multi-page flow"""
    # Initialize session
    _initialize_estimation_session(request)
    
    # Check if previous module is complete
    location_result = request.session.get('location_result')
    if not location_result:
        messages.warning(request, 'Please complete the Location module first.')
        return redirect('estimation_location')
    
    # Get appliances
    appliances = Appliance.objects.all().order_by('category', 'name')
    if not appliances.exists():
        messages.warning(request, 'No appliances available in the system. Please contact administrator.')
    
    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'calculate_energy':
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
                        messages.success(request, f'✅ Complete! System: {results["system_capacity_kw"]:.2f} kW, Annual Savings: PKR {results["annual_savings"]:.0f}, ROI: {results["roi_percentage"]:.1f}%')
                    else:
                        messages.error(request, 'Unable to calculate savings. Please check your inputs.')
            except Exception as e:
                messages.error(request, f'Error calculating savings: {str(e)}')
        
        # Save estimation to database
        elif action == 'save_estimation':
            try:
                location_result = request.session.get('location_result')
                energy_result = request.session.get('energy_result')
                roof_result = request.session.get('roof_result')
                savings_roi_result = request.session.get('savings_roi_result')
                
                if not (location_result and energy_result and roof_result and savings_roi_result):
                    messages.error(request, 'Please complete all estimation modules before saving.')
                else:
                    # Helper function to safely convert to Decimal
                    def safe_decimal(value, default=0):
                        try:
                            if value is None or value == '':
                                return Decimal(str(default))
                            return Decimal(str(value))
                        except (ValueError, TypeError, InvalidOperation):
                            return Decimal(str(default))
                    
                    # Safely convert all values
                    lat = safe_decimal(location_result.get('latitude'), 0)
                    lon = safe_decimal(location_result.get('longitude'), 0)
                    area = safe_decimal(roof_result.get('rooftop_area'), 0)
                    
                    # Check if already saved (prevent duplicates) - only if we have valid coordinates
                    existing = None
                    if lat and lon and area:
                        try:
                            existing = SolarEstimation.objects.filter(
                                user=request.user,
                                latitude=lat,
                                longitude=lon,
                                rooftop_area=area,
                                created_at__gte=timezone.now() - timedelta(minutes=5)
                            ).first()
                        except Exception:
                            existing = None
                    
                    if existing:
                        messages.info(request, 'This estimation was already saved recently.')
                    else:
                        # Create estimation with safe Decimal conversions
                        estimation = SolarEstimation.objects.create(
                            user=request.user,
                            latitude=lat,
                            longitude=lon,
                            address=location_result.get('address', ''),
                            city=location_result.get('city', ''),
                            state=location_result.get('state', ''),
                            monthly_consumption_kwh=safe_decimal(energy_result.get('total_monthly_kwh'), 0),
                            rooftop_length=safe_decimal(roof_result.get('rooftop_length'), 0),
                            rooftop_width=safe_decimal(roof_result.get('rooftop_width'), 0),
                            rooftop_area=area,
                            solar_irradiance=safe_decimal(location_result.get('irradiance'), 0),
                            panels_needed=int(savings_roi_result.get('panels_needed', 0)),
                            panel_capacity_kw=safe_decimal(savings_roi_result.get('system_capacity_kw'), 0),
                            estimated_cost=safe_decimal(savings_roi_result.get('total_installation_cost'), 0),
                            annual_savings=safe_decimal(savings_roi_result.get('annual_savings'), 0),
                            payback_period_years=safe_decimal(savings_roi_result.get('payback_period_years'), 0),
                            roi_percentage=safe_decimal(savings_roi_result.get('roi_percentage'), 0),
                            annual_energy_generated=safe_decimal(savings_roi_result.get('annual_energy_generated'), 0)
                        )
                        messages.success(request, '✅ Estimation saved successfully! You can view it in your dashboard.')
                        return redirect('solar_estimation')  # Refresh page to show saved status
            except Exception as e:
                messages.error(request, f'Error saving estimation: {str(e)}')
        
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
        
        elif action == 'clear_all':
            request.session['location_result'] = None
            request.session['energy_result'] = None
            request.session['roof_result'] = None
            request.session['savings_roi_result'] = None
            request.session.modified = True
            request.session.save()  # Force save
            messages.success(request, 'All estimation data cleared. You can start a new estimation.')
            return redirect('solar_estimation')
        
        return redirect('solar_estimation')
    
    # Check if all modules are complete
    all_complete = (
        request.session.get('location_result') and
        request.session.get('energy_result') and
        request.session.get('roof_result') and
        request.session.get('savings_roi_result')
    )
    
    # Calculate progress (0-100%)
    completed_modules = sum([
        1 if request.session.get('location_result') else 0,
        1 if request.session.get('energy_result') else 0,
        1 if request.session.get('roof_result') else 0,
        1 if request.session.get('savings_roi_result') else 0,
    ])
    progress_percentage = (completed_modules / 4) * 100
    
    # Check if current estimation is already saved (within last 5 minutes)
    estimation_saved = False
    if all_complete:
        try:
            location_result = request.session.get('location_result')
            energy_result = request.session.get('energy_result')
            roof_result = request.session.get('roof_result')
            if location_result and roof_result:
                # Safely convert to Decimal with validation
                def safe_decimal(value, default=0):
                    try:
                        if value is None or value == '':
                            return Decimal(str(default))
                        return Decimal(str(value))
                    except (ValueError, TypeError, InvalidOperation):
                        return Decimal(str(default))
                
                lat = safe_decimal(location_result.get('latitude'), 0)
                lon = safe_decimal(location_result.get('longitude'), 0)
                area = safe_decimal(roof_result.get('rooftop_area'), 0)
                
                # Only check if we have valid values
                if lat and lon and area:
                    recent_estimation = SolarEstimation.objects.filter(
                        user=request.user,
                        latitude=lat,
                        longitude=lon,
                        rooftop_area=area,
                        created_at__gte=timezone.now() - timedelta(minutes=5)
                    ).first()
                    if recent_estimation:
                        estimation_saved = True
        except Exception:
            # If check fails, assume not saved
            estimation_saved = False
    
    context = {
        'appliances': appliances,
        'location_result': request.session.get('location_result'),
        'energy_result': request.session.get('energy_result'),
        'roof_result': request.session.get('roof_result'),
        'savings_roi_result': request.session.get('savings_roi_result'),
        'all_complete': all_complete,
        'completed_modules': completed_modules,
        'progress_percentage': progress_percentage,
        'estimation_saved': estimation_saved,
    }
    
    return render(request, 'solar/solar_estimation.html', context)

def _initialize_estimation_session(request):
    """Helper function to initialize estimation session variables"""
    if 'location_result' not in request.session:
        request.session['location_result'] = None
    if 'energy_result' not in request.session:
        request.session['energy_result'] = None
    if 'roof_result' not in request.session:
        request.session['roof_result'] = None
    if 'savings_roi_result' not in request.session:
        request.session['savings_roi_result'] = None
    request.session.modified = True

def _get_estimation_progress(request):
    """Helper function to calculate estimation progress"""
    completed_modules = sum([
        1 if request.session.get('location_result') else 0,
        1 if request.session.get('energy_result') else 0,
        1 if request.session.get('roof_result') else 0,
        1 if request.session.get('savings_roi_result') else 0,
    ])
    progress_percentage = (completed_modules / 4) * 100
    return completed_modules, progress_percentage


@login_required
def estimation_energy(request):
    """Module 2: Energy Consumption Estimation - Multi-page flow"""
    # Initialize session
    _initialize_estimation_session(request)
    
    # Check if previous module is complete
    location_result = request.session.get('location_result')
    if not location_result:
        messages.warning(request, 'Please complete the Location module first.')
        return redirect('estimation_location')
    
    # Get appliances
    appliances = Appliance.objects.all().order_by('category', 'name')
    if not appliances.exists():
        messages.warning(request, 'No appliances available in the system. Please contact administrator.')
    
    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'calculate_energy':
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
                                daily_kwh = (appliance.power_rating_watts * quantity * hours_per_day) / 1000
                                monthly_kwh = daily_kwh * 30
                                total_monthly_kwh += monthly_kwh
                                
                                appliance_details.append({
                                    'appliance_name': appliance.name,
                                    'quantity': quantity,
                                    'hours_per_day': hours_per_day,
                                    'monthly_kwh': monthly_kwh
                                })
                        except (ValueError, TypeError):
                            continue
                
                if total_monthly_kwh > 0:
                    request.session['energy_result'] = {
                        'total_monthly_kwh': total_monthly_kwh,
                        'appliance_details': appliance_details
                    }
                    request.session.modified = True
                    messages.success(request, f'✅ Energy consumption calculated: {total_monthly_kwh:.2f} kWh/month')
                    # Stay on same page to show results
                else:
                    messages.error(request, 'Please select at least one appliance and set usage hours greater than 0.')
            except Exception as e:
                messages.error(request, f'Error calculating energy consumption: {str(e)}')
        
        elif action == 'clear_energy':
            request.session['energy_result'] = None
            request.session.modified = True
            messages.info(request, 'Energy results cleared.')
        
        elif action == 'clear_all':
            request.session['location_result'] = None
            request.session['energy_result'] = None
            request.session['roof_result'] = None
            request.session['savings_roi_result'] = None
            request.session.modified = True
            request.session.save()  # Force save
            messages.success(request, 'All estimation data cleared. Starting fresh.')
            return redirect('estimation_location')
    
    # Get progress and all results for navigation
    completed_modules, progress_percentage = _get_estimation_progress(request)
    energy_result = request.session.get('energy_result')
    roof_result = request.session.get('roof_result')
    savings_roi_result = request.session.get('savings_roi_result')
    
    context = {
        'appliances': appliances,
        'location_result': location_result,
        'energy_result': energy_result,
        'roof_result': roof_result,
        'savings_roi_result': savings_roi_result,
        'completed_modules': completed_modules,
        'progress_percentage': progress_percentage,
        'current_module': 2,
        'total_modules': 4,
    }
    return render(request, 'solar/estimation_energy.html', context)

@login_required
def estimation_roof(request):
    """Module 3: Roof Area Estimation - Multi-page flow"""
    # Initialize session
    _initialize_estimation_session(request)
    
    # Check if previous modules are complete
    location_result = request.session.get('location_result')
    energy_result = request.session.get('energy_result')
    if not location_result or not energy_result:
        messages.warning(request, 'Please complete the Location and Energy modules first.')
        if not location_result:
            return redirect('estimation_location')
        return redirect('estimation_energy')
    
    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'calculate_roof':
            try:
                rooftop_length = float(request.POST.get('rooftop_length', 0))
                rooftop_width = float(request.POST.get('rooftop_width', 0))
                
                if rooftop_length > 0 and rooftop_width > 0:
                    rooftop_area = rooftop_length * rooftop_width
                    panel_options = calculate_panel_capacity_options(rooftop_area)
                    
                    request.session['roof_result'] = {
                        'rooftop_length': rooftop_length,
                        'rooftop_width': rooftop_width,
                        'rooftop_area': rooftop_area,
                        'panel_options': panel_options
                    }
                    request.session.modified = True
                    messages.success(request, f'✅ Roof area calculated: {rooftop_area:.2f} m² with {len(panel_options)} panel options')
                    # Stay on same page to show results
                else:
                    messages.error(request, 'Please enter valid roof dimensions (must be greater than 0).')
            except (ValueError, TypeError) as e:
                messages.error(request, f'Invalid roof dimensions: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error calculating roof area: {str(e)}')
        
        elif action == 'clear_roof':
            request.session['roof_result'] = None
            request.session.modified = True
            messages.info(request, 'Roof results cleared.')
        
        elif action == 'clear_all':
            request.session['location_result'] = None
            request.session['energy_result'] = None
            request.session['roof_result'] = None
            request.session['savings_roi_result'] = None
            request.session.modified = True
            request.session.save()  # Force save
            messages.success(request, 'All estimation data cleared. Starting fresh.')
            return redirect('estimation_location')
    
    # Get progress and all results for navigation
    completed_modules, progress_percentage = _get_estimation_progress(request)
    roof_result = request.session.get('roof_result')
    savings_roi_result = request.session.get('savings_roi_result')
    
    context = {
        'location_result': location_result,
        'energy_result': energy_result,
        'roof_result': roof_result,
        'savings_roi_result': savings_roi_result,
        'completed_modules': completed_modules,
        'progress_percentage': progress_percentage,
        'current_module': 3,
        'total_modules': 4,
    }
    return render(request, 'solar/estimation_roof.html', context)

@login_required
def estimation_savings(request):
    """Module 4: Savings & ROI Calculation - Multi-page flow"""
    # Initialize session
    _initialize_estimation_session(request)
    
    # Check if previous modules are complete
    location_result = request.session.get('location_result')
    energy_result = request.session.get('energy_result')
    roof_result = request.session.get('roof_result')
    
    if not (location_result and energy_result and roof_result):
        messages.warning(request, 'Please complete all previous modules first.')
        if not location_result:
            return redirect('estimation_location')
        elif not energy_result:
            return redirect('estimation_energy')
        else:
            return redirect('estimation_roof')
    
    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'calculate_savings_roi':
            try:
                selected_option_index = int(request.POST.get('selected_panel_option', 0))
                electricity_rate = request.POST.get('electricity_rate')
                
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
                    messages.success(request, f'✅ Complete! System: {results["system_capacity_kw"]:.2f} kW, Annual Savings: PKR {results["annual_savings"]:.0f}, ROI: {results["roi_percentage"]:.1f}%')
                else:
                    messages.error(request, 'Unable to calculate savings. Please check your inputs.')
            except Exception as e:
                messages.error(request, f'Error calculating savings: {str(e)}')
        
        elif action == 'save_estimation':
            try:
                savings_roi_result = request.session.get('savings_roi_result')
                
                if not savings_roi_result:
                    messages.error(request, 'Please complete the calculation before saving.')
                else:
                    def safe_decimal(value, default=0):
                        try:
                            if value is None or value == '':
                                return Decimal(str(default))
                            return Decimal(str(value))
                        except (ValueError, TypeError, InvalidOperation):
                            return Decimal(str(default))
                    
                    lat = safe_decimal(location_result.get('latitude'), 0)
                    lon = safe_decimal(location_result.get('longitude'), 0)
                    area = safe_decimal(roof_result.get('rooftop_area'), 0)
                    
                    existing = None
                    if lat and lon and area:
                        try:
                            existing = SolarEstimation.objects.filter(
                                user=request.user,
                                latitude=lat,
                                longitude=lon,
                                rooftop_area=area,
                                created_at__gte=timezone.now() - timedelta(minutes=5)
                            ).first()
                        except Exception:
                            existing = None
                    
                    if existing:
                        messages.info(request, 'This estimation was already saved recently.')
                    else:
                        estimation = SolarEstimation.objects.create(
                            user=request.user,
                            latitude=lat,
                            longitude=lon,
                            address=location_result.get('address', ''),
                            city=location_result.get('city', ''),
                            state=location_result.get('state', ''),
                            monthly_consumption_kwh=safe_decimal(energy_result.get('total_monthly_kwh'), 0),
                            rooftop_length=safe_decimal(roof_result.get('rooftop_length'), 0),
                            rooftop_width=safe_decimal(roof_result.get('rooftop_width'), 0),
                            rooftop_area=area,
                            solar_irradiance=safe_decimal(location_result.get('irradiance'), 0),
                            panels_needed=int(savings_roi_result.get('panels_needed', 0)),
                            panel_capacity_kw=safe_decimal(savings_roi_result.get('system_capacity_kw'), 0),
                            estimated_cost=safe_decimal(savings_roi_result.get('total_installation_cost'), 0),
                            annual_savings=safe_decimal(savings_roi_result.get('annual_savings'), 0),
                            payback_period_years=safe_decimal(savings_roi_result.get('payback_period_years'), 0),
                            roi_percentage=safe_decimal(savings_roi_result.get('roi_percentage'), 0),
                            annual_energy_generated=safe_decimal(savings_roi_result.get('annual_energy_generated'), 0)
                        )
                        messages.success(request, '✅ Estimation saved successfully! You can view it in your dashboard.')
            except Exception as e:
                messages.error(request, f'Error saving estimation: {str(e)}')
        
        elif action == 'clear_savings_roi':
            request.session['savings_roi_result'] = None
            request.session.modified = True
            messages.info(request, 'Financial results cleared.')
        
        elif action == 'clear_all':
            request.session['location_result'] = None
            request.session['energy_result'] = None
            request.session['roof_result'] = None
            request.session['savings_roi_result'] = None
            request.session.modified = True
            messages.success(request, 'All estimation data cleared. You can start a new estimation.')
            return redirect('estimation_location')
    
    # Get progress
    completed_modules, progress_percentage = _get_estimation_progress(request)
    savings_roi_result = request.session.get('savings_roi_result')
    
    # Check if estimation is saved
    estimation_saved = False
    if savings_roi_result:
        try:
            lat = Decimal(str(location_result.get('latitude', 0)))
            lon = Decimal(str(location_result.get('longitude', 0)))
            area = Decimal(str(roof_result.get('rooftop_area', 0)))
            if lat and lon and area:
                recent_estimation = SolarEstimation.objects.filter(
                    user=request.user,
                    latitude=lat,
                    longitude=lon,
                    rooftop_area=area,
                    created_at__gte=timezone.now() - timedelta(minutes=5)
                ).first()
                if recent_estimation:
                    estimation_saved = True
        except Exception:
            estimation_saved = False
    
    context = {
        'location_result': location_result,
        'energy_result': energy_result,
        'roof_result': roof_result,
        'savings_roi_result': savings_roi_result,
        'completed_modules': completed_modules,
        'progress_percentage': progress_percentage,
        'estimation_saved': estimation_saved,
        'current_module': 4,
        'total_modules': 4,
    }
    return render(request, 'solar/estimation_savings.html', context)
@login_required
def estimation_history(request):
    """View estimation history - Only for regular users"""
    try:
        # Use raw SQL to get IDs first, avoiding Decimal conversion errors
        valid_ids = []
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM solar_solarestimation WHERE user_id = %s ORDER BY created_at DESC",
                    [request.user.id]
                )
                all_ids = [row[0] for row in cursor.fetchall()]
            
            # Validate each record individually
            for est_id in all_ids:
                try:
                    est = SolarEstimation.objects.get(id=est_id)
                    # Try to access all Decimal fields to validate
                    _ = est.latitude
                    _ = est.longitude
                    _ = est.monthly_consumption_kwh
                    _ = est.rooftop_length
                    _ = est.rooftop_width
                    _ = est.rooftop_area
                    _ = est.solar_irradiance
                    _ = est.panel_capacity_kw
                    _ = est.estimated_cost
                    _ = est.annual_savings
                    _ = est.payback_period_years
                    _ = est.roi_percentage
                    _ = est.annual_energy_generated
                    valid_ids.append(est_id)
                except (InvalidOperation, ValueError, TypeError, AttributeError):
                    # Skip invalid records
                    continue
        except Exception:
            # If raw SQL fails, try to get at least some records
            valid_ids = []
        
        # Load valid estimations and add safe display properties
        valid_estimations_list = []
        if valid_ids:
            try:
                estimations_queryset = SolarEstimation.objects.filter(id__in=valid_ids).order_by('-created_at')
                for est in estimations_queryset:
                    # Add safe display properties to avoid template errors
                    try:
                        est.safe_panel_capacity = f"{float(est.panel_capacity_kw):.1f} kW"
                    except (InvalidOperation, ValueError, TypeError, AttributeError):
                        est.safe_panel_capacity = "N/A"
                    
                    try:
                        est.safe_estimated_cost = f"PKR {float(est.estimated_cost):,.0f}"
                    except (InvalidOperation, ValueError, TypeError, AttributeError):
                        est.safe_estimated_cost = "N/A"
                    
                    try:
                        est.safe_annual_savings = f"PKR {float(est.annual_savings):,.0f}"
                    except (InvalidOperation, ValueError, TypeError, AttributeError):
                        est.safe_annual_savings = "N/A"
                    
                    try:
                        est.safe_roi = f"{float(est.roi_percentage):.1f}%"
                    except (InvalidOperation, ValueError, TypeError, AttributeError):
                        est.safe_roi = "N/A"
                    
                    try:
                        est.safe_payback = f"{float(est.payback_period_years):.1f} years"
                    except (InvalidOperation, ValueError, TypeError, AttributeError):
                        est.safe_payback = "N/A"
                    
                    valid_estimations_list.append(est)
            except Exception:
                valid_estimations_list = []
        
        # Try to calculate stats, but handle Decimal conversion errors
        try:
            if valid_estimations_list:
                # Calculate stats manually from valid records with safe conversion
                total_panels = 0
                total_cost = 0
                total_savings = 0
                count = 0
                
                for e in valid_estimations_list:
                    try:
                        total_panels += e.panels_needed if e.panels_needed else 0
                        total_cost += float(e.estimated_cost) if e.estimated_cost else 0
                        total_savings += float(e.annual_savings) if e.annual_savings else 0
                        count += 1
                    except (InvalidOperation, ValueError, TypeError):
                        continue
                
                if count > 0:
                    avg_panels_needed = total_panels / count
                    avg_estimated_cost = total_cost / count
                    avg_annual_savings = total_savings / count
                else:
                    avg_panels_needed = 0
                    avg_estimated_cost = 0
                    avg_annual_savings = 0
            else:
                avg_panels_needed = 0
                avg_estimated_cost = 0
                avg_annual_savings = 0
        except (InvalidOperation, ValueError, TypeError) as e:
            # If calculation fails, set defaults
            avg_panels_needed = 0
            avg_estimated_cost = 0
            avg_annual_savings = 0
        
        context = {
            'estimations': valid_estimations_list,
            'total_estimations': len(valid_estimations_list),
            'avg_panels_needed': round(avg_panels_needed, 1) if avg_panels_needed else 0,
            'avg_estimated_cost': round(avg_estimated_cost, 0) if avg_estimated_cost else 0,
            'avg_annual_savings': round(avg_annual_savings, 0) if avg_annual_savings else 0,
        }
        return render(request, 'solar/estimation_history.html', context)
    except Exception as e:
        # Log the error but don't show technical details to user
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error loading estimation history for user {request.user.id}: {str(e)}')
        
        messages.error(request, 'Unable to load estimation history. Please try again or contact support.')
        context = {
            'estimations': [],
            'total_estimations': 0,
            'avg_panels_needed': 0,
            'avg_estimated_cost': 0,
            'avg_annual_savings': 0,
        }
        return render(request, 'solar/estimation_history.html', context)

@login_required
def generate_estimation_report(request):
    """Generate a downloadable CSV report for the latest estimation."""
    try:
        # Prefer the most recent saved estimation
        estimation = SolarEstimation.objects.filter(user=request.user).order_by('-created_at').first()

        # If none saved, fall back to session data
        if not estimation:
            location_result = request.session.get('location_result')
            energy_result = request.session.get('energy_result')
            roof_result = request.session.get('roof_result')
            savings_roi_result = request.session.get('savings_roi_result')

            if not (location_result and energy_result and roof_result and savings_roi_result):
                messages.error(request, 'No estimation data found to generate report.')
                return redirect('solar_estimation')
            
            # Ensure session is saved
            request.session.modified = True

            # Prepare a CSV from session data
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="sun_savvy_estimation_report.csv"'
            response['Content-Type'] = 'text/csv; charset=utf-8'
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
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        filename = f'sun_savvy_estimation_{estimation.id}_{estimation.created_at.strftime("%Y%m%d")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Type'] = 'text/csv; charset=utf-8'
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
    """List all service providers with search, filter, and sort functionality"""
    # Get all verified providers
    providers = ServiceProvider.objects.filter(is_verified=True).select_related('user')
    
    # Search functionality - search by company name, city, or services
    search_query = request.GET.get('search', '').strip()
    if search_query:
        providers = providers.filter(
            Q(company_name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(state__icontains=search_query) |
            Q(services_offered__icontains=search_query)
        )
    
    # Filter by city
    city_filter = request.GET.get('city', '')
    if city_filter:
        providers = providers.filter(city__iexact=city_filter)
    
    # Filter by service type
    service_filter = request.GET.get('service', '')
    if service_filter:
        providers = providers.filter(services_offered__icontains=service_filter)
    
    # Sort options
    sort_by = request.GET.get('sort', 'rating')
    if sort_by == 'rating':
        providers = providers.order_by('-rating', '-created_at')
    elif sort_by == 'newest':
        providers = providers.order_by('-created_at')
    elif sort_by == 'name':
        providers = providers.order_by('company_name')
    else:
        providers = providers.order_by('-rating', '-created_at')
    
    # Get unique cities for filter dropdown
    all_cities = ServiceProvider.objects.filter(is_verified=True).values_list('city', flat=True).distinct().order_by('city')
    
    # Process providers to split services for display and convert rating
    providers_list = []
    for provider in providers:
        # Split services_offered by comma for display
        services_list = []
        if provider.services_offered:
            services_list = [s.strip() for s in provider.services_offered.split(',') if s.strip()]
        provider.services_list = services_list
        # Convert rating to integer for star display
        try:
            provider.rating_int = int(float(provider.rating))
        except (ValueError, TypeError, AttributeError):
            provider.rating_int = 0
        providers_list.append(provider)
    
    # Get total count
    total_count = len(providers_list)
    
    context = {
        'providers': providers_list,
        'search_query': search_query,
        'city_filter': city_filter,
        'service_filter': service_filter,
        'sort_by': sort_by,
        'all_cities': all_cities,
        'total_count': total_count,
    }
    return render(request, 'solar/service_providers.html', context)

def service_provider_detail(request, provider_id):
    """Service provider detail page"""
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    
    if request.method == 'POST' and request.user.is_authenticated:
        # Handle service request with new organized structure
        form = ServiceRequestForm(request.POST, provider=provider)
        if form.is_valid():
            sr = form.save(commit=False)
            sr.user = request.user
            sr.service_provider = provider
            # Set service_type based on request_category for backward compatibility
            category_map = {
                'purchase': 'Purchase',
                'installation': 'Installation',
                'repair': 'Repair',
                'maintenance': 'Maintenance',
            }
            sr.service_type = category_map.get(sr.request_category, sr.request_category or 'Service')
            sr.save()
            # Send email notification
            try:
                subject = 'New Service Request'
                category_display = dict(ServiceRequest.REQUEST_CATEGORY_CHOICES).get(sr.request_category, sr.request_category)
                body = f'You have a new service request from {request.user.get_full_name() or request.user.username}:\n' \
                       f'Request Type: {category_display}\n' \
                       f'Phone: {sr.phone}\n' \
                       f'Address: {sr.address}\n' \
                       f'Request ID: #{sr.id}'
                from_email = getattr(settings, 'EMAIL_HOST_USER', None) or 'no-reply@sunsavvy.local'
                recipient = [provider.email]
                send_mail(subject, body, from_email, recipient, fail_silently=True)
            except Exception:
                pass
            messages.success(request, 'Service request sent successfully!')
            return redirect('my_requests')
        else:
            # Form has errors, show them
            messages.error(request, 'Please correct the errors in the form.')
    
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

