from fastapi import APIRouter

router = APIRouter()

from app.routers.SAAdmin_backend.Admin_Notification_get import router as admin_notification_router
from app.routers.SAAdmin_backend.Admin_Alerts_Get_CameraAlerts import router as camera_alerts_router
from app.routers.SAAdmin_backend.Admin_Alerts_Submit_PushAlert import router as push_alert_router
from app.routers.SAAdmin_backend.Admin_Devices_Get_Submit_Post_Devices import router as devices_router
from app.routers.SAAdmin_backend.Admin_EmergencyContacts_Get import router as emergency_contacts_router
from app.routers.SAAdmin_backend.Admin_Get_dashboard import router as dashboard_router
from app.routers.SAAdmin_backend.Admin_Model_get import router as model_router
from app.routers.SAAdmin_backend.Admin_Register import router as register_router
from app.routers.SAAdmin_backend.admin_log_helper import router as log_helper_router
from app.routers.SAAdmin_backend.Admin_Reports_Get_Update_Reports import router as reports_router
from app.routers.SAAdmin_backend.Admin_Responders_Get_Update_Responders import router as responders_router
from app.routers.SAAdmin_backend.Admin_SystemConfig_Submit_Get_TipsResources import router as tipsresources_router
from app.routers.SAAdmin_backend.Admin_SystemConfig_Submit_Get_FAQ import router as faq_router
from app.routers.SAAdmin_backend.Admin_SystemConfig_Get_AdminProfile import router as admin_profile_router
from app.routers.SAAdmin_backend.AdminSystemConfig_SystemPreferences_get import router as system_prefs_router
from app.routers.SAAdmin_backend.AdminAlert_AlertGalery_Get import router as alert_gallery_router
from app.routers.SAAdmin_backend.Admin_SystemLogs_Get import router as system_logs_router
from app.routers.SAAdmin_backend.Admin_SystemConfig_Submit_ProfileUpdate import router as profile_update_router


from app.routers.SAAdmin_backend.GetAlerts import router as get_alerts_router

from app.routers.SAAdmin_backend.LogFetcherBackend import router as log_fetcher_router
from app.routers.SAAdmin_backend.Login import router as login_router
from app.routers.SAAdmin_backend.Logout import router as logout_router

from app.routers.SAAdmin_backend.SA_Dashboard import router as sa_dashboard_router
from app.routers.SAAdmin_backend.SA_Reports import router as sa_reports_router
from app.routers.SAAdmin_backend.SA_Logs import router as sa_logs_router
from app.routers.SAAdmin_backend.SA_log_helper import router as sa_log_helper_router
from app.routers.SAAdmin_backend.SA_gpdu_Emergency_contacts import router as sa_emergency_contacts_router
from app.routers.SAAdmin_backend.SA_Devices import router as sa_devices_router
from app.routers.SAAdmin_backend.Submit_Device_Integration import router as device_integration_router
from app.routers.SAAdmin_backend.submit_camera_alerts import router as submit_camera_alerts_router
from app.routers.SAAdmin_backend.SARegister import router as sa_register_router
from app.routers.SAAdmin_backend.SALogin import router as sa_login_router
from app.routers.SAAdmin_backend.SA_Users import router as sa_users_router
from app.routers.SAAdmin_backend.SALogin import router as sa_roles_router
router.include_router(sa_roles_router)
router.include_router(admin_notification_router)
router.include_router(camera_alerts_router)
router.include_router(push_alert_router)
router.include_router(devices_router)
router.include_router(emergency_contacts_router)
router.include_router(dashboard_router)
router.include_router(model_router)
router.include_router(register_router)
router.include_router(log_helper_router)
router.include_router(reports_router)
router.include_router(responders_router)
router.include_router(tipsresources_router)
router.include_router(faq_router)
router.include_router(admin_profile_router)
router.include_router(system_prefs_router)
router.include_router(alert_gallery_router)
router.include_router(system_logs_router)
router.include_router(profile_update_router)
router.include_router(get_alerts_router)
router.include_router(sa_dashboard_router)
router.include_router(log_fetcher_router)
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(sa_reports_router)
router.include_router(sa_logs_router)
router.include_router(sa_log_helper_router)
router.include_router(sa_emergency_contacts_router)
router.include_router(sa_devices_router)
router.include_router(device_integration_router)
router.include_router(submit_camera_alerts_router)
router.include_router(sa_register_router)
router.include_router(sa_login_router)
router.include_router(sa_users_router)

