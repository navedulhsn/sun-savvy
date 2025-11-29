"""
Utility functions for solar calculations and API integrations
"""
import requests
from decimal import Decimal
from django.conf import settings


def get_solar_irradiance(latitude, longitude):
    """
    Get solar irradiance data for a location
    Uses OpenWeather API as fallback if Solcast is not available
    """
    # Try Solcast API first
    if settings.SOLCAST_API_KEY:
        try:
            url = f"https://api.solcast.com.au/radiation/forecasts"
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'api_key': settings.SOLCAST_API_KEY
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Extract average irradiance
                if 'forecasts' in data and len(data['forecasts']) > 0:
                    avg_irradiance = sum(f.get('ghi', 0) for f in data['forecasts'][:24]) / 24
                    return Decimal(str(avg_irradiance))
        except Exception as e:
            print(f"Solcast API error: {e}")
    
    # Fallback to OpenWeather API
    if settings.OPENWEATHER_API_KEY:
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Estimate solar irradiance based on weather conditions
                # This is a simplified calculation
                cloud_coverage = data.get('clouds', {}).get('all', 50) / 100
                # Average solar irradiance ranges from 3-7 kWh/m²/day
                base_irradiance = Decimal('5.0')
                adjusted_irradiance = base_irradiance * (1 - cloud_coverage * 0.5)
                return adjusted_irradiance
        except Exception as e:
            print(f"OpenWeather API error: {e}")
    
    # Default fallback value (average for Pakistan)
    return Decimal('5.0')


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


def calculate_savings_roi(location_result, energy_result, roof_result, selected_panel_option_index=0, electricity_rate=None, provider_rates=None):
    """
    Comprehensive Savings & ROI Calculation
    Uses results from Location, Energy, and Roof modules
    
    Args:
        location_result: dict with irradiance data
        energy_result: dict with monthly consumption
        roof_result: dict with panel options
        selected_panel_option_index: which panel option to use (default: 0 = recommended)
        electricity_rate: custom electricity rate per kWh (optional)
        provider_rates: dict with 'price_per_watt' and 'installation_cost_per_watt' (optional)
    """
    if not (location_result and energy_result and roof_result):
        return None
    
    # Get selected panel option
    panel_options = roof_result.get('panel_options', [])
    if not panel_options or selected_panel_option_index >= len(panel_options):
        return None
    
    selected_option = panel_options[selected_panel_option_index]
    
    # Get data from modules
    irradiance = Decimal(str(location_result.get('irradiance', 5.0)))
    monthly_consumption_kwh = Decimal(str(energy_result.get('total_monthly_kwh', 0)))
    rooftop_area = Decimal(str(roof_result.get('rooftop_area', 0)))
    
    # Panel specifications
    max_panels = selected_option.get('max_panels', 0)
    panel_specs = selected_option.get('panel_specs', {})
    
    # Handle both dict format and direct access
    if panel_specs:
        panel_area = Decimal(str(panel_specs.get('area_sqm', 2.0)))
        panel_power = panel_specs.get('power_watts', 400)
        panel_efficiency = Decimal(str(panel_specs.get('efficiency', 0.20)))
        # Use provider rate if available, otherwise use default
        if provider_rates and 'price_per_watt' in provider_rates:
             panel_cost_per_panel = Decimal(str(provider_rates['price_per_watt'])) * panel_power
        else:
             panel_cost_per_panel = Decimal(str(panel_specs.get('cost_per_panel', 240)))
    else:
        # Fallback to defaults if panel_specs is missing
        panel_area = Decimal('2.0')
        panel_power = 400
        panel_efficiency = Decimal('0.20')
        panel_cost_per_panel = Decimal('240')
    
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
    panel_cost = Decimal(str(panels_needed)) * panel_cost_per_panel
    
    # Installation and additional costs
    if provider_rates and 'installation_cost_per_watt' in provider_rates:
        installation_cost_per_watt = Decimal(str(provider_rates['installation_cost_per_watt']))
    else:
        installation_cost_per_watt = Decimal('0.30')
        
    installation_cost = (panels_needed * panel_power * installation_cost_per_watt)
    
    inverter_cost = system_capacity_kw * Decimal('200')
    wiring_mounting = system_capacity_kw * Decimal('100')
    permits_inspection = system_capacity_kw * Decimal('50')
    
    total_installation_cost = panel_cost + installation_cost + inverter_cost + wiring_mounting + permits_inspection
    
    # Electricity rate (default or custom)
    if electricity_rate is None:
        electricity_rate = Decimal('0.12')  # $0.12 per kWh default
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
    """
    return [
        {
            'name': 'Small Panel',
            'power_watts': 250,
            'length_m': 1.65,
            'width_m': 0.99,
            'area_sqm': 1.63,
            'efficiency': 0.15,
            'cost_per_panel': 150,
        },
        {
            'name': 'Medium Panel',
            'power_watts': 400,
            'length_m': 2.00,
            'width_m': 1.00,
            'area_sqm': 2.00,
            'efficiency': 0.20,
            'cost_per_panel': 240,
        },
        {
            'name': 'Large Panel',
            'power_watts': 500,
            'length_m': 2.20,
            'width_m': 1.10,
            'area_sqm': 2.42,
            'efficiency': 0.22,
            'cost_per_panel': 300,
        },
        {
            'name': 'Premium Panel',
            'power_watts': 600,
            'length_m': 2.40,
            'width_m': 1.20,
            'area_sqm': 2.88,
            'efficiency': 0.25,
            'cost_per_panel': 400,
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
            total_cost = max_panels * panel_type['cost_per_panel']
            
            options.append({
                'panel_type': panel_type['name'],
                'panel_specs': panel_type,
                'max_panels': max_panels,
                'total_capacity_kw': float(total_capacity_kw),
                'total_cost': total_cost,
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
            return {
                'fault_type': 'Error',
                'confidence_score': 0.0,
                'description': 'AI Model not found.',
                'recommendations': 'Please contact administrator.'
            }

        # Load model
        model = load_model(model_path)
        
        # Preprocess image
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        
        # Predict
        predictions = model.predict(img_array)
        class_indices = {0: 'Bird-drop', 1: 'Clean', 2: 'Dusty', 3: 'Electrical-damage', 4: 'Physical-Damage', 5: 'Snow-Covered'}
        predicted_class_index = np.argmax(predictions)
        fault_type = class_indices.get(predicted_class_index, 'Unknown')
        confidence = float(predictions[0][predicted_class_index])
        
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
        
    except Exception as e:
        print(f"AI Detection Error: {e}")
        return {
            'fault_type': 'Error',
            'confidence_score': 0.0,
            'description': f'Error during analysis: {str(e)}',
            'recommendations': 'Try uploading a clearer image.'
        }

