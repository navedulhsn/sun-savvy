from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class SolarEstimation(models.Model):
    """Stores user solar estimation calculations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)  # For anonymous users
    
    # Location data
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    # Energy consumption
    monthly_consumption_kwh = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Rooftop dimensions
    rooftop_length = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    rooftop_width = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    rooftop_area = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Calculated results
    solar_irradiance = models.DecimalField(max_digits=10, decimal_places=2)
    panels_needed = models.IntegerField()
    panel_capacity_kw = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    annual_savings = models.DecimalField(max_digits=12, decimal_places=2)
    payback_period_years = models.DecimalField(max_digits=5, decimal_places=2)
    roi_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    annual_energy_generated = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Estimation for {self.address} - {self.created_at}"


class Appliance(models.Model):
    """Common household appliances for energy consumption calculation"""
    name = models.CharField(max_length=100)
    power_rating_watts = models.IntegerField()
    hours_per_day = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    quantity = models.IntegerField(default=1)
    category = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name
    
    def daily_consumption_kwh(self):
        return (self.power_rating_watts * self.hours_per_day * self.quantity) / 1000
