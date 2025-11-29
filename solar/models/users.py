from django.db import models
from django.contrib.auth.models import User

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
    
    # Pricing fields
    price_per_watt = models.DecimalField(max_digits=5, decimal_places=2, default=0.50, help_text="Price per watt in USD")
    installation_cost_per_watt = models.DecimalField(max_digits=5, decimal_places=2, default=0.30, help_text="Installation cost per watt in USD")
    
    # Profile completeness and business info
    company_logo = models.ImageField(upload_to='provider_logos/', blank=True, null=True)
    business_description = models.TextField(blank=True, help_text="Describe your business and services")
    years_in_business = models.IntegerField(default=0, help_text="Years of experience")
    business_hours = models.CharField(max_length=200, blank=True, help_text="e.g., Mon-Fri 9AM-5PM")
    website = models.URLField(blank=True)
    
    # Service areas
    service_areas = models.TextField(blank=True, help_text="Cities/regions you serve, comma-separated")
    service_radius = models.IntegerField(default=50, help_text="Service radius in miles")
    
    # Credentials and certifications
    license_number = models.CharField(max_length=100, blank=True)
    certifications = models.TextField(blank=True, help_text="List your certifications")
    insurance_verified = models.BooleanField(default=False)
    
    # Profile completeness tracking
    profile_complete = models.BooleanField(default=False)
    profile_completion_percentage = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_profile_completion(self):
        """Calculate profile completion percentage"""
        fields_to_check = [
            self.company_logo,
            self.business_description,
            self.years_in_business > 0,
            self.business_hours,
            self.service_areas,
            self.license_number,
            self.certifications,
            self.price_per_watt > 0,
            self.installation_cost_per_watt > 0,
        ]
        completed = sum(1 for field in fields_to_check if field)
        percentage = int((completed / len(fields_to_check)) * 100)
        self.profile_completion_percentage = percentage
        self.profile_complete = percentage >= 80
        return percentage
    
    def __str__(self):
        return self.company_name


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
