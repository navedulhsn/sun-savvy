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
