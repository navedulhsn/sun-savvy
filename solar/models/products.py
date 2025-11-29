from django.db import models
from .users import ServiceProvider


class ProviderPanel(models.Model):
    """Provider-specific solar panel/product listing"""
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='panels')
    name = models.CharField(max_length=200)
    power_watts = models.IntegerField()
    efficiency = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Panel efficiency in fraction, e.g., 0.20")
    price_pkr = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price in PKR")
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
