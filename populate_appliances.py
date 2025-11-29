"""
Script to populate the database with common household appliances
Run with: python manage.py shell < populate_appliances.py
"""

from solar.models import Appliance

# Clear existing appliances
Appliance.objects.all().delete()

appliances_data = [
    # Kitchen Appliances
    {'name': 'Refrigerator', 'power_rating_watts': 150, 'category': 'Kitchen'},
    {'name': 'Microwave Oven', 'power_rating_watts': 1200, 'category': 'Kitchen'},
    {'name': 'Electric Stove', 'power_rating_watts': 2000, 'category': 'Kitchen'},
    {'name': 'Dishwasher', 'power_rating_watts': 1800, 'category': 'Kitchen'},
    {'name': 'Coffee Maker', 'power_rating_watts': 1000, 'category': 'Kitchen'},
    {'name': 'Toaster', 'power_rating_watts': 800, 'category': 'Kitchen'},
    {'name': 'Blender', 'power_rating_watts': 300, 'category': 'Kitchen'},
    {'name': 'Electric Kettle', 'power_rating_watts': 1500, 'category': 'Kitchen'},
    
    # Cooling & Heating
    {'name': 'Air Conditioner (1 Ton)', 'power_rating_watts': 1200, 'category': 'Cooling & Heating'},
    {'name': 'Air Conditioner (1.5 Ton)', 'power_rating_watts': 1800, 'category': 'Cooling & Heating'},
    {'name': 'Air Conditioner (2 Ton)', 'power_rating_watts': 2400, 'category': 'Cooling & Heating'},
    {'name': 'Ceiling Fan', 'power_rating_watts': 75, 'category': 'Cooling & Heating'},
    {'name': 'Table Fan', 'power_rating_watts': 50, 'category': 'Cooling & Heating'},
    {'name': 'Space Heater', 'power_rating_watts': 1500, 'category': 'Cooling & Heating'},
    {'name': 'Water Heater (Geyser)', 'power_rating_watts': 2000, 'category': 'Cooling & Heating'},
    
    # Lighting
    {'name': 'LED Bulb (10W)', 'power_rating_watts': 10, 'category': 'Lighting'},
    {'name': 'LED Bulb (15W)', 'power_rating_watts': 15, 'category': 'Lighting'},
    {'name': 'CFL Bulb (20W)', 'power_rating_watts': 20, 'category': 'Lighting'},
    {'name': 'Tube Light (40W)', 'power_rating_watts': 40, 'category': 'Lighting'},
    {'name': 'Incandescent Bulb (60W)', 'power_rating_watts': 60, 'category': 'Lighting'},
    
    # Entertainment
    {'name': 'LED TV (32 inch)', 'power_rating_watts': 50, 'category': 'Entertainment'},
    {'name': 'LED TV (42 inch)', 'power_rating_watts': 80, 'category': 'Entertainment'},
    {'name': 'LED TV (55 inch)', 'power_rating_watts': 120, 'category': 'Entertainment'},
    {'name': 'Desktop Computer', 'power_rating_watts': 200, 'category': 'Entertainment'},
    {'name': 'Laptop', 'power_rating_watts': 60, 'category': 'Entertainment'},
    {'name': 'Gaming Console', 'power_rating_watts': 150, 'category': 'Entertainment'},
    {'name': 'Sound System', 'power_rating_watts': 100, 'category': 'Entertainment'},
    
    # Laundry
    {'name': 'Washing Machine', 'power_rating_watts': 500, 'category': 'Laundry'},
    {'name': 'Dryer', 'power_rating_watts': 3000, 'category': 'Laundry'},
    {'name': 'Iron', 'power_rating_watts': 1000, 'category': 'Laundry'},
    
    # Other
    {'name': 'Vacuum Cleaner', 'power_rating_watts': 1000, 'category': 'Other'},
    {'name': 'Hair Dryer', 'power_rating_watts': 1500, 'category': 'Other'},
    {'name': 'Water Pump', 'power_rating_watts': 750, 'category': 'Other'},
    {'name': 'Wi-Fi Router', 'power_rating_watts': 10, 'category': 'Other'},
    {'name': 'Phone Charger', 'power_rating_watts': 5, 'category': 'Other'},
]

# Create appliances
created_count = 0
for data in appliances_data:
    appliance, created = Appliance.objects.get_or_create(
        name=data['name'],
        defaults={
            'power_rating_watts': data['power_rating_watts'],
            'category': data['category']
        }
    )
    if created:
        created_count += 1

print(f"✅ Successfully created {created_count} appliances!")
print(f"📊 Total appliances in database: {Appliance.objects.count()}")
print("\nAppliances by category:")
from django.db.models import Count
categories = Appliance.objects.values('category').annotate(count=Count('id')).order_by('category')
for cat in categories:
    print(f"  - {cat['category']}: {cat['count']} appliances")
