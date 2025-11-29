from django.db import models
from django.contrib.auth.models import User

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
