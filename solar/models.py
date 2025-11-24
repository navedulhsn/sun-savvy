from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class UserProfile(models.Model):
    """Extended user profile for end users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"


class ServiceProvider(models.Model):
    """Service provider model for solar installers and repairers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    services_offered = models.CharField(
        max_length=200,
        help_text="e.g., Installation, Repair, Maintenance"
    )
    is_verified = models.BooleanField(default=False)  # Admin verification
    email_verified = models.BooleanField(default=False)  # Email verification
    verification_token = models.CharField(max_length=100, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.company_name


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


class FaultDetection(models.Model):
    """Stores AI fault detection results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='fault_detections/')
    detection_result = models.JSONField(default=dict)
    fault_type = models.CharField(max_length=100, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Fault Detection - {self.fault_type} ({self.created_at})"


class AuthorizedPerson(models.Model):
    """Authorized person model for admin/authorized personnel"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    designation = models.CharField(max_length=100, help_text="e.g., Admin, Manager, Supervisor")
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.full_name} ({self.designation})"


class ServiceRequest(models.Model):
    """Service requests from users to service providers"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='requests')
    service_type = models.CharField(max_length=100)  # Installation, Repair, Maintenance
    description = models.TextField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_date = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    quote_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-requested_date']
    
    def __str__(self):
        return f"{self.service_type} request from {self.user.username} to {self.service_provider.company_name}"

