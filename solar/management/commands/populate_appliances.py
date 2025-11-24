"""
Management command to populate default appliances
Run: python manage.py populate_appliances
"""
from django.core.management.base import BaseCommand
from solar.models import Appliance


class Command(BaseCommand):
    help = 'Populate default appliances for energy consumption calculation'

    def handle(self, *args, **options):
        appliances_data = [
            # Kitchen Appliances
            {'name': 'Refrigerator', 'power_rating_watts': 150, 'hours_per_day': 24, 'quantity': 1, 'category': 'Kitchen'},
            {'name': 'Microwave Oven', 'power_rating_watts': 1000, 'hours_per_day': 0.5, 'quantity': 1, 'category': 'Kitchen'},
            {'name': 'Electric Stove', 'power_rating_watts': 2000, 'hours_per_day': 1, 'quantity': 1, 'category': 'Kitchen'},
            {'name': 'Dishwasher', 'power_rating_watts': 1200, 'hours_per_day': 1, 'quantity': 1, 'category': 'Kitchen'},
            {'name': 'Coffee Maker', 'power_rating_watts': 800, 'hours_per_day': 0.5, 'quantity': 1, 'category': 'Kitchen'},
            
            # Living Room
            {'name': 'Television', 'power_rating_watts': 150, 'hours_per_day': 4, 'quantity': 1, 'category': 'Living Room'},
            {'name': 'Air Conditioner', 'power_rating_watts': 2000, 'hours_per_day': 8, 'quantity': 1, 'category': 'Living Room'},
            {'name': 'Ceiling Fan', 'power_rating_watts': 75, 'hours_per_day': 12, 'quantity': 3, 'category': 'Living Room'},
            {'name': 'LED Lights', 'power_rating_watts': 10, 'hours_per_day': 6, 'quantity': 10, 'category': 'Living Room'},
            
            # Bedroom
            {'name': 'Laptop', 'power_rating_watts': 50, 'hours_per_day': 6, 'quantity': 1, 'category': 'Bedroom'},
            {'name': 'Desktop Computer', 'power_rating_watts': 200, 'hours_per_day': 4, 'quantity': 1, 'category': 'Bedroom'},
            {'name': 'Phone Charger', 'power_rating_watts': 5, 'hours_per_day': 3, 'quantity': 3, 'category': 'Bedroom'},
            
            # Laundry
            {'name': 'Washing Machine', 'power_rating_watts': 500, 'hours_per_day': 1, 'quantity': 1, 'category': 'Laundry'},
            {'name': 'Clothes Dryer', 'power_rating_watts': 3000, 'hours_per_day': 0.5, 'quantity': 1, 'category': 'Laundry'},
            {'name': 'Iron', 'power_rating_watts': 1000, 'hours_per_day': 0.5, 'quantity': 1, 'category': 'Laundry'},
            
            # Other
            {'name': 'Water Heater', 'power_rating_watts': 3000, 'hours_per_day': 2, 'quantity': 1, 'category': 'Other'},
            {'name': 'Water Pump', 'power_rating_watts': 750, 'hours_per_day': 1, 'quantity': 1, 'category': 'Other'},
        ]
        
        created_count = 0
        updated_count = 0
        
        for appliance_data in appliances_data:
            appliance, created = Appliance.objects.get_or_create(
                name=appliance_data['name'],
                defaults=appliance_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {appliance.name}'))
            else:
                # Update existing appliance
                for key, value in appliance_data.items():
                    setattr(appliance, key, value)
                appliance.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated: {appliance.name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully populated appliances!\n'
            f'Created: {created_count}\n'
            f'Updated: {updated_count}\n'
            f'Total: {Appliance.objects.count()}'
        ))

