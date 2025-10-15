from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.routers.responder_backend.config import get_db_conn

# Create the main router for responder backend
router = APIRouter()


# --- Direct Endpoints (login/register) ---

class ResponderLogin(BaseModel):
    username: str
    password: str

@router.post("/login_responder")
def login_responder(data: ResponderLogin):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, full_name FROM responders WHERE username=%s AND password=%s",
            (data.username, data.password)
        )
        user = cursor.fetchone()
        if user:
            return {"success": True, "responder_id": user[0], "full_name": user[1]}
        else:
            return {"success": False, "message": "Invalid username or password."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

class ResponderRegister(BaseModel):
    full_name: str
    email: str
    phone: str
    username: str
    password: str
    role: str = "Responder"

@router.post("/register_responder")
def register_responder(data: ResponderRegister):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO responders (full_name, email, phone, username, password, role) VALUES (%s, %s, %s, %s, %s, %s)",
            (data.full_name, data.email, data.phone, data.username, data.password, data.role)
        )
        conn.commit()
        return {"success": True, "message": "Responder registered successfully."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# --- Include all sub-routers ---
from app.routers.responder_backend.profile_update_details import router as profile_update_router
from app.routers.responder_backend.profile_get_details import router as profile_get_router
from app.routers.responder_backend.responder_submit_report import router as submit_router
from app.routers.responder_backend.get_responder_profile import router as profile_router
from app.routers.responder_backend.get_alert import router as alert_router
from app.routers.responder_backend.submit_alert_action import router as action_router
from app.routers.responder_backend.get_ongoing_reports import router as ongoing_router
from app.routers.responder_backend.get_history_reports import router as history_router
from app.routers.responder_backend.get_approve_reports import router as approve_router
from app.routers.responder_backend.get_notification import router as notification_router
from app.routers.responder_backend.messaging_api import router as messaging_router
from app.routers.responder_backend.submit_patrolling import router as patrolling_router
from app.routers.responder_backend.submit_registration import router as submit_registration_router
from app.routers.responder_backend.get_tipsresources import router as tipsresources_router
from app.routers.responder_backend.get_EmergencyContacts import router as emergencycontacts_router
from app.routers.responder_backend.get_reports import router as reports_router
from app.routers.responder_backend.home_get_logs import router as logs_router
from app.routers.responder_backend.login import router as login_router
from app.routers.responder_backend.settings_get_FAQ import router as faq_router
from app.routers.responder_backend.settings_get_profile import router as get_profile_router
from app.routers.responder_backend.settings_update_profile import router as update_profile_router
from app.routers.responder_backend.settings_update_password import router as update_password_router
from app.routers.responder_backend.conversation_api import router as conversation_router

# Attach all routers to the main responder router
router.include_router(profile_update_router)
router.include_router(profile_get_router)
router.include_router(submit_router)
router.include_router(profile_router)
router.include_router(alert_router)
router.include_router(action_router)
router.include_router(ongoing_router)
router.include_router(history_router)
router.include_router(approve_router)
router.include_router(notification_router)
router.include_router(messaging_router)
router.include_router(patrolling_router)
router.include_router(submit_registration_router)
router.include_router(tipsresources_router)
router.include_router(emergencycontacts_router)
router.include_router(reports_router)
router.include_router(logs_router)
router.include_router(login_router)
router.include_router(faq_router)
router.include_router(get_profile_router)
router.include_router(update_profile_router)
router.include_router(update_password_router)
router.include_router(conversation_router)