from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register_selection, name='register'),
    path('register/user/', views.register_user, name='register_user'),
    path('register/provider/', views.register_service_provider, name='register_service_provider'),
    path('register/authorized/', views.register_authorized_person, name='register_authorized_person'),
    path('login/', views.login_view, name='login'),
    path('logout/',views.logout_view, name='logout'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('provider/profile/edit/', views.provider_profile_edit, name='provider_profile_edit'),
    path('provider/requests/', views.provider_requests, name='provider_requests'),
    path('provider/requests/<int:request_id>/', views.provider_request_detail, name='provider_request_detail'),
    path('provider/services/', views.provider_services, name='provider_services'),
    path('provider/panels/', views.provider_panels, name='provider_panels'),
    path('provider/panels/add/', views.provider_panel_add, name='provider_panel_add'),
    path('provider/panels/<int:panel_id>/edit/', views.provider_panel_edit, name='provider_panel_edit'),
    path('provider/panels/<int:panel_id>/delete/', views.provider_panel_delete, name='provider_panel_delete'),
    # Note: Admin dashboard URLs are now in sunsavvy/urls.py to avoid conflicts with Django admin
    
    # Solar Estimation
    path('estimation/', views.solar_estimation, name='solar_estimation'),  # Redirects to first module
    path('estimation/location/', views.estimation_location, name='estimation_location'),
    path('estimation/energy/', views.estimation_energy, name='estimation_energy'),
    path('estimation/roof/', views.estimation_roof, name='estimation_roof'),
    path('estimation/savings/', views.estimation_savings, name='estimation_savings'),
    path('estimation/history/', views.estimation_history, name='estimation_history'),
    path('estimation/generate-report/', views.generate_estimation_report, name='generate_estimation_report'),
    
    # Service Providers
    path('providers/', views.service_providers, name='service_providers'),
    path('providers/<int:provider_id>/', views.service_provider_detail, name='service_provider_detail'),
    path('my-requests/', views.my_requests, name='my_requests'),
    
    # Fault Detection
    path('fault-detection/', views.fault_detection, name='fault_detection'),
    path('fault-detection/history/', views.fault_detection_history, name='fault_detection_history'),
    
    # Chatbot
    path('api/chatbot/', views.chatbot, name='chatbot'),
]

