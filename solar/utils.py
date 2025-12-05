"""
Utility functions for solar calculations and API integrations
"""
import requests
from decimal import Decimal
from django.conf import settings
import json


def validate_coordinates(latitude, longitude):
    """
    Validate latitude and longitude coordinates
    Returns (is_valid, error_message)
    """
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        # Check global ranges
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90 degrees."
        if not (-180 <= lng <= 180):
            return False, "Longitude must be between -180 and 180 degrees."
        
        # Check Pakistan boundaries (approximate)
        # Pakistan: lat 23.5 to 37.0, lng 60.8 to 77.8
        if not (23.5 <= lat <= 37.0) or not (60.8 <= lng <= 77.8):
            return False, "Coordinates are outside Pakistan. Please enter a location within Pakistan."
        
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid coordinate format. Please enter valid numbers."


def validate_pakistan_location(latitude, longitude):
    """
    Check if coordinates are within Pakistan boundaries
    """
    try:
        lat = float(latitude)
        lng = float(longitude)
        return (23.5 <= lat <= 37.0) and (60.8 <= lng <= 77.8)
    except (ValueError, TypeError):
        return False


def geocode_address(address, city, state):
    """
    Geocode an address to get coordinates using free OpenStreetMap Nominatim API
    Falls back to Google Maps if API key is available
    Address parameter is optional - can geocode with just city and state
    Returns (success, latitude, longitude, formatted_address, error_message)
    """
    # Build full address string (address is optional)
    if address:
        full_address = f"{address}, {city}, {state}, Pakistan"
    else:
        full_address = f"{city}, {state}, Pakistan"
    
    # Try OpenStreetMap Nominatim first (FREE, no key required)
    try:
        import time
        # Rate limiting: Nominatim requires 1 request per second
        time.sleep(1)  # Simple rate limiting
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': full_address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'pk',  # Restrict to Pakistan
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'SunSavvy Solar Estimation App'  # Required by Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                lat = float(result.get('lat', 0))
                lng = float(result.get('lon', 0))
                formatted_address = result.get('display_name', full_address)
                
                # Validate coordinates are in Pakistan
                if validate_pakistan_location(lat, lng):
                    return True, lat, lng, formatted_address, None
                else:
                    return False, None, None, None, "Address geocoded but location is outside Pakistan."
            else:
                # No results from Nominatim, try Google Maps as fallback if key available
                pass
        else:
            # Nominatim failed, try Google Maps as fallback if key available
            pass
    except Exception as e:
        print(f"OpenStreetMap Nominatim error: {e}")
        # Continue to Google Maps fallback
    
    # Fallback to Google Maps if API key is available
    if settings.GOOGLE_MAPS_API_KEY:
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': full_address,
                'key': settings.GOOGLE_MAPS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('results'):
                    result = data['results'][0]
                    location = result['geometry']['location']
                    lat = location['lat']
                    lng = location['lng']
                    formatted_address = result.get('formatted_address', full_address)
                    
                    # Validate coordinates are in Pakistan
                    if validate_pakistan_location(lat, lng):
                        return True, lat, lng, formatted_address, None
                    else:
                        return False, None, None, None, "Address geocoded but location is outside Pakistan."
        except Exception as e:
            print(f"Google Maps geocoding error: {e}")
    
    return False, None, None, None, "Could not geocode address. Please try entering coordinates manually."


def reverse_geocode(latitude, longitude):
    """
    Reverse geocode coordinates to get address using free OpenStreetMap Nominatim API
    Falls back to Google Maps if API key is available
    Returns (success, formatted_address, city, state, error_message)
    """
    # Try OpenStreetMap Nominatim first (FREE, no key required)
    try:
        import time
        # Rate limiting: Nominatim requires 1 request per second
        time.sleep(1)  # Simple rate limiting
        
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'SunSavvy Solar Estimation App'  # Required by Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and 'address' in data:
                address_data = data.get('address', {})
                formatted_address = data.get('display_name', '')
                
                # Extract city and state from address components
                city = address_data.get('city') or address_data.get('town') or address_data.get('village') or ''
                state = address_data.get('state') or address_data.get('region') or ''
                
                return True, formatted_address, city, state, None
            else:
                # No results from Nominatim, try Google Maps as fallback if key available
                pass
        else:
            # Nominatim failed, try Google Maps as fallback if key available
            pass
    except Exception as e:
        print(f"OpenStreetMap Nominatim reverse geocoding error: {e}")
        # Continue to Google Maps fallback
    
    # Fallback to Google Maps if API key is available
    if settings.GOOGLE_MAPS_API_KEY:
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'latlng': f"{latitude},{longitude}",
                'key': settings.GOOGLE_MAPS_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('results'):
                    result = data['results'][0]
                    formatted_address = result.get('formatted_address', '')
                    
                    # Extract city and state from address components
                    city = ''
                    state = ''
                    for component in result.get('address_components', []):
                        types = component.get('types', [])
                        if 'locality' in types or 'administrative_area_level_2' in types:
                            city = component.get('long_name', '')
                        if 'administrative_area_level_1' in types:
                            state = component.get('long_name', '')
                    
                    return True, formatted_address, city, state, None
        except Exception as e:
            print(f"Google Maps reverse geocoding error: {e}")
    
    return False, None, None, None, "Could not reverse geocode coordinates. Address fields will remain empty."


def analyze_location_with_gemini(address, city, state, latitude=None, longitude=None):
    """
    Use Gemini API to analyze location and provide insights (OPTIONAL - has fallback)
    Returns dict with analysis results
    """
    # If no Gemini API key, return a basic analysis based on location
    if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
        # Fallback: Provide basic location analysis without API
        location_name = f"{city}, {state}" if city and state else address or "Unknown location"
        
        # Basic climate zone estimation for Pakistan based on coordinates
        climate_zone = "Semi-arid"
        if latitude and longitude:
            if latitude > 30:  # Northern regions
                climate_zone = "Temperate"
            elif latitude < 25:  # Southern regions
                climate_zone = "Arid"
        
        return {
            'success': True,
            'error': None,
            'location_summary': f"{location_name} is located in Pakistan. This area has good solar potential for panel installation.",
            'climate_zone': climate_zone,
            'irradiance_estimate': 5.5,  # Average for Pakistan
            'recommendations': 'Standard solar panel installation recommended. Ensure proper orientation and minimal shading.'
        }
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        # Build prompt
        location_info = f"Address: {address}, City: {city}, State: {state}, Pakistan"
        if latitude and longitude:
            location_info += f", Coordinates: {latitude}, {longitude}"
        
        prompt = f"""Analyze this location in Pakistan for solar panel installation:
{location_info}

Provide a brief analysis in JSON format with:
1. location_summary: A 2-3 sentence summary of the location
2. climate_zone: Climate classification (e.g., "Arid", "Semi-arid", "Tropical")
3. irradiance_estimate: Estimated daily solar irradiance in kWh/m²/day (typical range 4-7 for Pakistan)
4. recommendations: 2-3 key recommendations for solar installation at this location

Return ONLY valid JSON, no markdown formatting."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response (remove markdown if present)
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        analysis = json.loads(response_text)
        
        return {
            'success': True,
            'error': None,
            'location_summary': analysis.get('location_summary', ''),
            'climate_zone': analysis.get('climate_zone', 'Unknown'),
            'irradiance_estimate': analysis.get('irradiance_estimate', 5.0),
            'recommendations': analysis.get('recommendations', '')
        }
    
    except ImportError:
        return {
            'success': False,
            'error': 'Google Generative AI library not installed. Install with: pip install google-generativeai',
            'location_summary': None,
            'climate_zone': None,
            'irradiance_estimate': None,
            'recommendations': None
        }
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract info from text
        return {
            'success': True,
            'error': None,
            'location_summary': response_text[:200] if 'response_text' in locals() else 'Location analysis completed.',
            'climate_zone': 'Unknown',
            'irradiance_estimate': 5.0,
            'recommendations': 'Standard solar installation recommended.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Gemini API error: {str(e)}',
            'location_summary': None,
            'climate_zone': None,
            'irradiance_estimate': None,
            'recommendations': None
        }


def get_solar_irradiance_nasa_power(latitude, longitude):
    """
    Get solar irradiance from NASA POWER API (free, no key required)
    Returns (success, irradiance_value, error_message)
    """
    try:
        # NASA POWER API endpoint
        url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        params = {
            'parameters': 'ALLSKY_SFC_SW_DWN',  # All-sky surface shortwave downward irradiance
            'community': 'RE',
            'longitude': longitude,
            'latitude': latitude,
            'start': '20230101',  # Start date (recent year)
            'end': '20231231',   # End date
            'format': 'JSON'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract irradiance data
            if 'properties' in data and 'parameter' in data['properties']:
                param_data = data['properties']['parameter'].get('ALLSKY_SFC_SW_DWN', {})
                
                if 'values' in param_data:
                    values = [v for v in param_data['values'].values() if v is not None]
                    if values:
                        # Convert from MJ/m²/day to kWh/m²/day
                        # 1 MJ = 0.277778 kWh
                        avg_mj = sum(values) / len(values)
                        avg_kwh = avg_mj * 0.277778
                        return True, Decimal(str(avg_kwh)), None
        
        return False, None, "NASA POWER API returned no data."
    
    except Exception as e:
        return False, None, f"NASA POWER API error: {str(e)}"


def get_solar_irradiance(latitude, longitude):
    """
    Get solar irradiance data for a location using multiple sources
    Priority: Solcast > NASA POWER > OpenWeather > Gemini AI > Database > Default
    Returns dict with irradiance value and source information
    """
    result = {
        'irradiance': None,
        'source': None,
        'confidence': 'low',
        'error': None
    }
    
    # 1. Try Solcast API (most accurate, requires key)
    if settings.SOLCAST_API_KEY:
        try:
            url = "https://api.solcast.com.au/radiation/forecasts"
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'api_key': settings.SOLCAST_API_KEY,
                'format': 'json'
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'forecasts' in data and len(data['forecasts']) > 0:
                    # Calculate average GHI (Global Horizontal Irradiance) for next 24 hours
                    ghi_values = [f.get('ghi', 0) for f in data['forecasts'][:24] if f.get('ghi') is not None]
                    if ghi_values:
                        # Convert from W/m² to kWh/m²/day
                        avg_ghi_w = sum(ghi_values) / len(ghi_values)
                        avg_ghi_kwh = (avg_ghi_w * 24) / 1000  # Convert to kWh/m²/day
                        result['irradiance'] = Decimal(str(avg_ghi_kwh))
                        result['source'] = 'Solcast API'
                        result['confidence'] = 'high'
                        return result
        except Exception as e:
            print(f"Solcast API error: {e}")
    
    # 2. Try NASA POWER API (free, reliable historical data)
    nasa_success, nasa_irradiance, nasa_error = get_solar_irradiance_nasa_power(latitude, longitude)
    if nasa_success and nasa_irradiance:
        result['irradiance'] = nasa_irradiance
        result['source'] = 'NASA POWER API'
        result['confidence'] = 'high'
        return result
    
    # 3. Try OpenWeatherMap API (current weather-based estimate)
    if settings.OPENWEATHER_API_KEY:
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                cloud_coverage = data.get('clouds', {}).get('all', 50) / 100
                # Base irradiance for Pakistan (typically 5-6 kWh/m²/day)
                base_irradiance = Decimal('5.5')
                # Adjust based on cloud coverage
                adjusted_irradiance = base_irradiance * (1 - cloud_coverage * 0.4)
                result['irradiance'] = adjusted_irradiance
                result['source'] = 'OpenWeatherMap API'
                result['confidence'] = 'medium'
                return result
        except Exception as e:
            print(f"OpenWeather API error: {e}")
    
    # 4. Try database lookup for major Pakistani cities
    pakistan_cities_irradiance = {
        'karachi': Decimal('5.8'),
        'lahore': Decimal('5.5'),
        'islamabad': Decimal('5.2'),
        'faisalabad': Decimal('5.6'),
        'rawalpindi': Decimal('5.3'),
        'multan': Decimal('5.7'),
        'peshawar': Decimal('5.4'),
        'quetta': Decimal('6.0'),
        'sialkot': Decimal('5.5'),
        'hyderabad': Decimal('5.7'),
    }
    
    # This would need city name from reverse geocoding, skip for now
    
    # 5. Random irradiance fallback for Pakistan (4.8 to 5.5 kWh/m²/day)
    # This ensures we always return a valid result even if all APIs fail
    import random
    random_irradiance = Decimal(str(round(random.uniform(4.8, 5.5), 2)))
    result['irradiance'] = random_irradiance
    result['source'] = 'Random (Pakistan Range)'
    result['confidence'] = 'low'
    result['error'] = 'All APIs unavailable. Using random value for Pakistan (4.8-5.5 kWh/m²/day).'
    
    return result


def calculate_solar_potential(irradiance, rooftop_area):
    """
    Calculate solar energy potential based on irradiance and rooftop area
    Returns annual energy generation in kWh
    """
    # Standard solar panel efficiency (around 20%)
    panel_efficiency = Decimal('0.20')
    # System losses (wiring, inverter, etc.) - typically 15-20%
    system_losses = Decimal('0.15')
    
    # Daily energy generation per m²
    daily_energy_per_sqm = irradiance * panel_efficiency * (1 - system_losses)
    
    # Annual energy generation
    annual_energy = daily_energy_per_sqm * rooftop_area * Decimal('365')
    
    return annual_energy


def calculate_panels_needed(monthly_consumption, annual_energy_per_panel):
    """
    Calculate number of solar panels needed
    Assumes standard 400W panels
    """
    # Annual consumption
    annual_consumption = monthly_consumption * Decimal('12')
    
    # Add 20% buffer for system losses and future needs
    required_annual_generation = annual_consumption * Decimal('1.20')
    
    # Calculate panels needed
    panels_needed = (required_annual_generation / annual_energy_per_panel).quantize(Decimal('1'))
    
    return int(panels_needed) if panels_needed > 0 else 1


def calculate_financial_analysis(panels_needed, annual_energy_generated, monthly_consumption):
    """
    Calculate ROI, payback period, and savings
    """
    # Standard panel specifications
    panel_wattage = Decimal('400')  # 400W per panel
    panel_cost_per_watt = Decimal('0.50')  # $0.50 per watt (adjust based on market)
    installation_cost_per_watt = Decimal('0.30')  # Installation cost
    
    # Total system capacity
    system_capacity_kw = (panels_needed * panel_wattage) / Decimal('1000')
    
    # Cost calculations
    panel_cost = panels_needed * panel_wattage * panel_cost_per_watt
    installation_cost = panels_needed * panel_wattage * installation_cost_per_watt
    inverter_cost = system_capacity_kw * Decimal('200')  # Inverter cost
    other_costs = system_capacity_kw * Decimal('100')  # Wiring, mounting, etc.
    
    estimated_cost = panel_cost + installation_cost + inverter_cost + other_costs
    
    # Savings calculation
    # Average electricity rate (adjust based on region)
    electricity_rate_per_kwh = Decimal('0.12')  # $0.12 per kWh
    
    # Annual savings
    annual_consumption = monthly_consumption * Decimal('12')
    annual_savings = min(annual_energy_generated, annual_consumption) * electricity_rate_per_kwh
    
    # Payback period
    if annual_savings > 0:
        payback_period = estimated_cost / annual_savings
    else:
        payback_period = Decimal('0')
    
    # ROI (25-year system lifetime)
    system_lifetime = Decimal('25')
    total_savings = annual_savings * system_lifetime
    net_profit = total_savings - estimated_cost
    roi_percentage = (net_profit / estimated_cost * Decimal('100')) if estimated_cost > 0 else Decimal('0')
    
    return {
        'estimated_cost': estimated_cost,
        'annual_savings': annual_savings,
        'payback_period_years': payback_period,
        'roi_percentage': roi_percentage,
        'system_capacity_kw': system_capacity_kw,
    }


def calculate_savings_roi(location_result, energy_result, roof_result, selected_panel_option_index=0, electricity_rate=None):
    """
    Comprehensive Savings & ROI Calculation
    Uses results from Location, Energy, and Roof modules
    Based on rough estimation using Pakistani market rates (2024-2025)
    
    Args:
        location_result: dict with irradiance data
        energy_result: dict with monthly consumption
        roof_result: dict with panel options
        selected_panel_option_index: which panel option to use (default: 0 = recommended)
        electricity_rate: custom electricity rate per kWh in PKR (optional, default: 33.6 PKR/kWh)
    """
    if not (location_result and energy_result and roof_result):
        return None
    
    # Get selected panel option
    panel_options = roof_result.get('panel_options', [])
    if not panel_options or selected_panel_option_index >= len(panel_options):
        return None
    
    selected_option = panel_options[selected_panel_option_index]
    
    # Get data from modules
    # Handle both old format (direct Decimal) and new format (dict with irradiance key)
    irradiance_value = location_result.get('irradiance', 5.0)
    if isinstance(irradiance_value, dict):
        irradiance = Decimal(str(irradiance_value.get('irradiance', 5.0)))
    else:
        irradiance = Decimal(str(irradiance_value))
    monthly_consumption_kwh = Decimal(str(energy_result.get('total_monthly_kwh', 0)))
    rooftop_area = Decimal(str(roof_result.get('rooftop_area', 0)))
    
    # Panel specifications
    max_panels = selected_option.get('max_panels', 0)
    panel_specs = selected_option.get('panel_specs', {})
    
    # Handle both dict format and direct access
    # Use Pakistani market rates from panel specs
    if panel_specs:
        panel_area = Decimal(str(panel_specs.get('area_sqm', 2.0)))
        panel_power = panel_specs.get('power_watts', 400)
        panel_efficiency = Decimal(str(panel_specs.get('efficiency', 0.20)))
        # Use panel cost from specs (Pakistani market rates in PKR)
        # Get cost_per_panel from panel_specs, with proper fallback
        cost_from_specs = panel_specs.get('cost_per_panel')
        if cost_from_specs is not None:
            panel_cost_per_panel = Decimal(str(cost_from_specs))
        else:
            # Fallback to Medium panel cost if not specified
            panel_cost_per_panel = Decimal('20000')  # Medium panel cost in PKR
    else:
        # Fallback to defaults if panel_specs is missing
        panel_area = Decimal('2.0')
        panel_power = 400
        panel_efficiency = Decimal('0.20')
        panel_cost_per_panel = Decimal('20000')  # Default: Medium panel cost in PKR
    
    # Calculate actual panels needed based on consumption
    annual_consumption = monthly_consumption_kwh * Decimal('12')
    
    # Calculate annual energy generation per panel
    system_losses = Decimal('0.15')  # 15% system losses
    daily_energy_per_panel = irradiance * panel_efficiency * (1 - system_losses) * panel_area
    annual_energy_per_panel = daily_energy_per_panel * Decimal('365')
    
    # Calculate panels needed (with 20% buffer)
    required_annual_generation = annual_consumption * Decimal('1.20')
    panels_needed = int((required_annual_generation / annual_energy_per_panel).quantize(Decimal('1'), rounding='ROUND_UP'))
    
    # Don't exceed available roof space
    panels_needed = min(panels_needed, max_panels)
    
    if panels_needed == 0:
        panels_needed = 1
    
    # Calculate total system capacity
    system_capacity_kw = (panels_needed * panel_power) / Decimal('1000')
    
    # Calculate total annual energy generation
    total_panel_area = Decimal(str(panels_needed)) * panel_area
    annual_energy_generated = calculate_solar_potential(irradiance, total_panel_area)
    
    # Cost calculations
    # Panel cost: panels_needed * cost_per_panel
    panel_cost = Decimal(str(panels_needed)) * panel_cost_per_panel
    
    # Installation and additional costs (Pakistani market rates)
    # Installation cost per watt in PKR (reduced to 30-40 PKR per watt for labor only, since panel cost already includes hardware)
    installation_cost_per_watt_pkr = Decimal('35')  # Installation labor cost in PKR per watt
    installation_cost = (panels_needed * panel_power * installation_cost_per_watt_pkr)
    
    # Additional costs in PKR (Pakistani market rates)
    inverter_cost = system_capacity_kw * Decimal('40000')  # ~140 USD per kW = 40,000 PKR
    wiring_mounting = system_capacity_kw * Decimal('20000')  # ~70 USD per kW = 20,000 PKR
    permits_inspection = Decimal('0')  # Free permits in Pakistan
    
    # Total cost = Panel cost + Installation labor + Additional equipment
    total_installation_cost = panel_cost + installation_cost + inverter_cost + wiring_mounting + permits_inspection
    
    # Electricity rate (default or custom) - in PKR
    if electricity_rate is None:
        electricity_rate = Decimal('33.6')  # Default PKR per kWh (Pakistan average)
    else:
        electricity_rate = Decimal(str(electricity_rate))
    
    # Savings calculation
    monthly_savings = min(annual_energy_generated / Decimal('12'), monthly_consumption_kwh) * electricity_rate
    annual_savings = monthly_savings * Decimal('12')
    
    # Payback period (Total Cost ÷ Annual Savings)
    if annual_savings > 0:
        payback_period_years = total_installation_cost / annual_savings
        payback_period_months = payback_period_years * Decimal('12')
    else:
        payback_period_years = Decimal('0')
        payback_period_months = Decimal('0')
    
    # ROI calculation (25-year system lifetime)
    system_lifetime_years = Decimal('25')
    total_savings_over_lifetime = annual_savings * system_lifetime_years
    net_profit = total_savings_over_lifetime - total_installation_cost
    
    # ROI = (Net Profit / Total Cost) × 100
    if total_installation_cost > 0:
        roi_percentage = (net_profit / total_installation_cost) * Decimal('100')
    else:
        roi_percentage = Decimal('0')
    
    # Additional metrics
    monthly_cost_savings_percentage = (monthly_savings / (monthly_consumption_kwh * electricity_rate)) * Decimal('100') if monthly_consumption_kwh > 0 else Decimal('0')
    
    return {
        'panels_needed': panels_needed,
        'system_capacity_kw': float(system_capacity_kw),
        'annual_energy_generated': float(annual_energy_generated),
        'annual_consumption': float(annual_consumption),
        
        # Cost breakdown
        'panel_cost': float(panel_cost),
        'installation_cost': float(installation_cost),
        'inverter_cost': float(inverter_cost),
        'wiring_mounting_cost': float(wiring_mounting),
        'permits_inspection_cost': float(permits_inspection),
        'total_installation_cost': float(total_installation_cost),
        
        # Savings
        'monthly_savings': float(monthly_savings),
        'annual_savings': float(annual_savings),
        'total_savings_over_lifetime': float(total_savings_over_lifetime),
        'monthly_cost_savings_percentage': float(monthly_cost_savings_percentage),
        
        # ROI & Payback
        'payback_period_years': float(payback_period_years),
        'payback_period_months': float(payback_period_months),
        'roi_percentage': float(roi_percentage),
        'net_profit': float(net_profit),
        
        # System info
        'system_lifetime_years': 25,
        'electricity_rate_per_kwh': float(electricity_rate),
        'selected_panel_type': selected_option.get('panel_type', 'N/A'),
    }


def get_panel_types():
    """
    Returns available solar panel types with their specifications
    Based on Pakistani market rates (PKR) as of 2024-2025
    Prices are per panel (not total)
    """
    return [
        {
            'name': 'Standard Panel',
            'power_watts': 250,
            'length_m': 1.65,
            'width_m': 0.99,
            'area_sqm': 1.63,
            'efficiency': 0.15,
            'cost_per_panel': 15000,  # PKR per panel - Standard quality panels
        },
        {
            'name': 'Medium Panel',
            'power_watts': 400,
            'length_m': 2.00,
            'width_m': 1.00,
            'area_sqm': 2.00,
            'efficiency': 0.20,
            'cost_per_panel': 20000,  # PKR per panel - Good quality panels
        },
        {
            'name': 'Large Panel',
            'power_watts': 500,
            'length_m': 2.20,
            'width_m': 1.10,
            'area_sqm': 2.42,
            'efficiency': 0.22,
            'cost_per_panel': 25000,  # PKR per panel - High quality panels
        },
        {
            'name': 'Premium Panel',
            'power_watts': 600,
            'length_m': 2.40,
            'width_m': 1.20,
            'area_sqm': 2.88,
            'efficiency': 0.25,
            'cost_per_panel': 30000,  # PKR per panel - Premium/Tier-1 panels
        },
    ]


def calculate_panel_capacity_options(rooftop_area):
    """
    Calculate how many panels of each type can fit on the rooftop
    Returns list of options with panel counts, capacity, and cost
    """
    # Convert to Decimal if it's not already
    if not isinstance(rooftop_area, Decimal):
        rooftop_area = Decimal(str(rooftop_area))
    
    panel_types = get_panel_types()
    options = []
    
    # Reserve 20% space for gaps, mounting, and safety margins
    usable_area = rooftop_area * Decimal('0.80')
    
    for panel_type in panel_types:
        panel_area = Decimal(str(panel_type['area_sqm']))
        max_panels = int((usable_area / panel_area).quantize(Decimal('1'), rounding='ROUND_DOWN'))
        
        if max_panels > 0:
            total_capacity_kw = (max_panels * panel_type['power_watts']) / Decimal('1000')
            cost_per_panel = Decimal(str(panel_type['cost_per_panel']))  # Price of ONE panel
            total_cost = max_panels * cost_per_panel  # Total cost for all panels
            
            # Calculate kW per panel for display
            kw_per_panel = panel_type['power_watts'] / 1000.0
            
            options.append({
                'panel_type': panel_type['name'],
                'panel_specs': panel_type,
                'max_panels': max_panels,
                'cost_per_panel': float(cost_per_panel),  # Price of ONE panel
                'kw_per_panel': kw_per_panel,  # kW per panel for display
                'total_capacity_kw': float(total_capacity_kw),
                'total_cost': float(total_cost),  # Total cost for all panels
                'area_used': float(max_panels * panel_area),
                'area_utilization': float((max_panels * panel_area / rooftop_area) * 100),
            })
    
    # Sort by capacity (highest first)
    options.sort(key=lambda x: x['total_capacity_kw'], reverse=True)
    return options


def calculate_appliance_consumption(selected_appliances):
    """
    Calculate monthly energy consumption from selected appliances
    selected_appliances: list of dicts with 'appliance_id', 'quantity', 'hours_per_day'
    """
    from .models import Appliance
    
    total_monthly_kwh = Decimal('0')
    appliance_details = []
    
    for item in selected_appliances:
        try:
            appliance = Appliance.objects.get(id=item['appliance_id'])
            quantity = int(item.get('quantity', 1))
            hours_per_day = Decimal(str(item.get('hours_per_day', 0)))
            
            # Daily consumption in kWh
            daily_kwh = (appliance.power_rating_watts * hours_per_day * quantity) / Decimal('1000')
            monthly_kwh = daily_kwh * Decimal('30')
            
            total_monthly_kwh += monthly_kwh
            
            appliance_details.append({
                'appliance': appliance,
                'quantity': quantity,
                'hours_per_day': float(hours_per_day),
                'monthly_kwh': float(monthly_kwh),
            })
        except Appliance.DoesNotExist:
            continue
    
    return {
        'total_monthly_kwh': float(total_monthly_kwh),
        'appliance_details': appliance_details,
    }


def detect_fault_ai(image_path):
    """
    AI-based fault detection for solar panels using VGG16
    Falls back to basic image analysis if model is not available
    """
    try:
        import numpy as np
        from tensorflow.keras.models import load_model
        from tensorflow.keras.preprocessing import image
        from django.conf import settings
        import os

        # Path to the model
        model_path = os.path.join(settings.BASE_DIR, 'ai_models', 'physical_fault_detection_vgg16_finetuned.h5')
        
        if not os.path.exists(model_path):
            # Fallback: Return a basic analysis result
            print(f"Model not found at {model_path}. Using fallback analysis.")
            return {
                'fault_type': 'Clean',
                'confidence_score': 0.75,  # Medium confidence for fallback
                'description': 'AI model not available. Basic analysis: Image uploaded successfully. For accurate fault detection, please ensure the AI model is properly configured.',
                'recommendations': 'Upload a clear, well-lit image of your solar panel for best results. Contact administrator if issues persist.'
            }
        
        print(f"Loading AI model from: {model_path}")

        # Load model
        try:
            print("Loading TensorFlow model...")
            model = load_model(model_path)
            print("Model loaded successfully!")
        except Exception as model_error:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error loading model: {error_trace}")
            return {
                'fault_type': 'Error',
                'confidence_score': 0.0,
                'description': f'Model loading error: {str(model_error)}. Please ensure TensorFlow is installed and the model file is valid.',
                'recommendations': 'Install TensorFlow: pip install tensorflow. If error persists, check model file integrity.'
            }
        
        # Preprocess image
        try:
            img = image.load_img(image_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array /= 255.0
        except Exception as img_error:
            print(f"Image preprocessing error: {img_error}")
            return {
                'fault_type': 'Error',
                'confidence_score': 0.0,
                'description': f'Error processing image: {str(img_error)}',
                'recommendations': 'Please upload a valid image file (JPG, PNG).'
            }
        
        # Predict
        try:
            print("Running AI prediction...")
            predictions = model.predict(img_array, verbose=0)  # Suppress verbose output
            class_indices = {0: 'Bird-drop', 1: 'Clean', 2: 'Dusty', 3: 'Electrical-damage', 4: 'Physical-Damage', 5: 'Snow-Covered'}
            predicted_class_index = np.argmax(predictions[0])
            fault_type = class_indices.get(predicted_class_index, 'Unknown')
            confidence = float(predictions[0][predicted_class_index])  # Confidence score (0-1)
            print(f"Prediction complete: {fault_type} (confidence: {confidence:.2f})")
        except Exception as predict_error:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Prediction error: {error_trace}")
            return {
                'fault_type': 'Error',
                'confidence_score': 0.0,
                'description': f'Error during AI prediction: {str(predict_error)}',
                'recommendations': 'Try uploading a clearer image or contact administrator.'
            }
        
        descriptions = {
            'Bird-drop': 'Bird droppings detected. This can create hot spots and reduce efficiency.',
            'Clean': 'Panel appears clean and in good condition.',
            'Dusty': 'Dust accumulation detected. Cleaning is recommended to restore efficiency.',
            'Electrical-damage': 'Potential electrical damage detected. Professional inspection required immediately.',
            'Physical-Damage': 'Physical damage (cracks/breakage) detected. Panel may need replacement.',
            'Snow-Covered': 'Snow coverage detected. Remove snow to restore power generation.'
        }
        
        recommendations = {
            'Bird-drop': 'Clean the panel with water and a soft sponge.',
            'Clean': 'Continue regular monitoring.',
            'Dusty': 'Wash the panels with water.',
            'Electrical-damage': 'Contact a certified solar technician for inspection.',
            'Physical-Damage': 'Contact your installer for warranty or replacement options.',
            'Snow-Covered': 'Carefully remove snow using a soft roof rake.'
        }

        return {
            'fault_type': fault_type,
            'confidence_score': confidence,
            'description': descriptions.get(fault_type, 'Analysis complete.'),
            'recommendations': recommendations.get(fault_type, 'Regular maintenance recommended.')
        }
        
    except ImportError as import_error:
        # TensorFlow or other dependencies not installed
        print(f"Import error (TensorFlow may not be installed): {import_error}")
        return {
            'fault_type': 'Clean',
            'confidence_score': 0.70,
            'description': 'AI model dependencies not available. Basic analysis: Image uploaded successfully. For full AI detection, please install TensorFlow and configure the model.',
            'recommendations': 'Contact administrator to set up AI model dependencies (TensorFlow).'
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"AI Detection Error: {error_trace}")
        return {
            'fault_type': 'Error',
            'confidence_score': 0.0,
            'description': f'Error during analysis: {str(e)}',
            'recommendations': 'Try uploading a clearer image or contact administrator for assistance.'
        }

