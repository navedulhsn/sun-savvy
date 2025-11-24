"""
URL configuration for sunsavvy project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from solar import views

urlpatterns = [
    # Custom admin dashboard URLs - must be BEFORE Django admin to avoid conflicts
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/providers/', views.admin_providers, name='admin_providers'),
    path('admin/providers/<int:provider_id>/', views.admin_provider_detail, name='admin_provider_detail'),
    path('admin/providers/<int:provider_id>/approve/', views.admin_provider_approve, name='admin_provider_approve'),
    path('admin/providers/<int:provider_id>/delete/', views.admin_provider_delete, name='admin_provider_delete'),
    path('admin/requests/', views.admin_requests, name='admin_requests'),
    path('admin/requests/<int:request_id>/', views.admin_request_detail, name='admin_request_detail'),
    path('admin/requests/<int:request_id>/update-status/', views.admin_request_update_status, name='admin_request_update_status'),
    
    # Django admin (catch-all should be after specific admin routes)
    path('admin/', admin.site.urls),
    
    # All other solar app URLs
    path('', include('solar.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Static files are automatically served by Django in DEBUG mode from STATICFILES_DIRS

