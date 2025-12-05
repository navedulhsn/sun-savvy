from django.db import models
from django.contrib.auth.models import User
from .users import ServiceProvider

class ServiceRequest(models.Model):
    """Service requests from users to service providers"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Request category - what user wants
    REQUEST_CATEGORY_CHOICES = [
        ('purchase', 'Purchase Panels'),
        ('installation', 'Installation Service'),
        ('repair', 'Repair Service'),
        ('maintenance', 'Maintenance Service'),
    ]
    
    # Panel type choices - same 4 types as ProviderPanel
    PANEL_TYPE_CHOICES = [
        ('premium', 'Premium Solar Panel'),
        ('large', 'Large Solar Panel'),
        ('medium', 'Medium Solar Panel'),
        ('standard', 'Standard Solar Panel'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='requests')
    request_category = models.CharField(max_length=20, choices=REQUEST_CATEGORY_CHOICES, blank=True, null=True, help_text="Main request type")
    service_type = models.CharField(max_length=100, blank=True)  # Legacy field, kept for compatibility
    preferred_panel_type = models.CharField(max_length=20, choices=PANEL_TYPE_CHOICES, blank=True, null=True, help_text="Panel type for installation/maintenance")
    selected_panel = models.ForeignKey('ProviderPanel', on_delete=models.SET_NULL, null=True, blank=True, help_text="Selected panel for purchase")
    quantity = models.IntegerField(default=1, help_text="Quantity for purchase")
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
