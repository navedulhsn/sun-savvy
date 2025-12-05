from django.db import models
from .users import ServiceProvider


class ProviderPanel(models.Model):
    """Provider-specific solar panel/product listing"""
    # Predefined panel type choices - 4 types only
    PANEL_TYPE_CHOICES = [
        ('premium', 'Premium Solar Panel'),
        ('large', 'Large Solar Panel'),
        ('medium', 'Medium Solar Panel'),
        ('standard', 'Standard Solar Panel'),
    ]
    
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='panels')
    panel_type = models.CharField(max_length=20, choices=PANEL_TYPE_CHOICES, blank=True, null=True, help_text="Select panel type")
    name = models.CharField(max_length=200, blank=True)  # Optional custom name
    model_no = models.CharField(max_length=100, blank=True, help_text="Model number or SKU")
    power_watts = models.IntegerField()
    efficiency = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Panel efficiency in fraction, e.g., 0.20")
    length = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Length in meters")
    width = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Width in meters")
    price_pkr = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price in PKR")
    installation_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Installation price in PKR")
    stock = models.IntegerField(default=0)
    warranty_years = models.IntegerField(default=0, help_text="Warranty period in years")
    image = models.ImageField(upload_to='provider_panels/', null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.power_watts}W) - {self.provider.company_name}" 
