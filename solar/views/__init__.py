from .common_views import home
from .auth_views import (
    login_view, logout_view, register_selection, register_user, 
    register_service_provider, register_authorized_person, verify_email,
    is_authorized_person
)
from .customer_views import (
    dashboard, solar_estimation, estimation_history, 
    generate_estimation_report, my_requests, service_providers, 
    service_provider_detail
)
from .provider_views import (
    provider_dashboard,
    provider_profile_edit,
    provider_requests,
    provider_request_detail,
    provider_services,
)
from .admin_views import (
    admin_dashboard, admin_users, admin_user_detail, admin_user_delete,
    admin_providers, admin_provider_detail, admin_provider_approve, 
    admin_provider_delete, admin_requests, admin_request_detail, 
    admin_request_update_status
)
from .ai_views import fault_detection, fault_detection_history, chatbot
