from django.contrib import admin
from .models import (
    UserProfile, ServiceProvider, AuthorizedPerson, SolarEstimation, 
    Appliance, FaultDetection, ServiceRequest, ProviderPanel
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'city', 'is_verified', 'rating', 'created_at']
    list_filter = ['is_verified', 'city', 'state']
    search_fields = ['company_name', 'user__username', 'email', 'city']
    list_editable = ['is_verified']


@admin.register(AuthorizedPerson)
class AuthorizedPersonAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'designation', 'email', 'email_verified', 'is_active', 'created_at']
    list_filter = ['email_verified', 'is_active', 'designation', 'created_at']
    search_fields = ['full_name', 'user__username', 'email', 'designation']
    list_editable = ['is_active']


@admin.register(SolarEstimation)
class SolarEstimationAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'city', 'panels_needed', 'estimated_cost', 'created_at']
    list_filter = ['city', 'state', 'created_at']
    search_fields = ['user__username', 'address', 'city']
    readonly_fields = ['created_at']


@admin.register(Appliance)
class ApplianceAdmin(admin.ModelAdmin):
    list_display = ['name', 'power_rating_watts', 'hours_per_day', 'quantity', 'category']
    list_filter = ['category']
    search_fields = ['name', 'category']


@admin.register(FaultDetection)
class FaultDetectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'fault_type', 'confidence_score', 'created_at']
    list_filter = ['fault_type', 'created_at']
    search_fields = ['user__username', 'fault_type']
    readonly_fields = ['created_at']


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'service_provider', 'service_type', 'status', 'requested_date']
    list_filter = ['status', 'service_type', 'requested_date']
    search_fields = ['user__username', 'service_provider__company_name', 'service_type']
    readonly_fields = ['requested_date']


@admin.register(ProviderPanel)
class ProviderPanelAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'power_watts', 'price_pkr', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'provider']
    search_fields = ['name', 'provider__company_name']
    list_editable = ['is_active', 'stock']

