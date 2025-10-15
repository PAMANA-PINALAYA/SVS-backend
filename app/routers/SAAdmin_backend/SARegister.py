from fastapi import APIRouter
from app.routers.SAAdmin_backend.db_connection import db_manager

router = APIRouter()

@router.post("/superadmin/register")
def superadmin_register(email: str, password: str, full_name: str, admin_key: str, photo: str = "policeman.png"):
    success = db_manager.register_superadmin(email, password, full_name, admin_key, photo)
    if success:
        return {"success": True, "message": "SuperAdmin registered successfully."}
    else:
        return {"success": False, "message": "Registration failed. Email may already exist."}