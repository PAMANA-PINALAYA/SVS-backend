from fastapi import APIRouter
from pydantic import BaseModel   # <-- ADD THIS LINE
from app.routers.SAAdmin_backend.db_connection import db_manager

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    admin_key: str
    photo: str = "policeman.png"

@router.post("/superadmin/register")
def superadmin_register(data: RegisterRequest):
    success = db_manager.register_superadmin(
        data.email, data.password, data.full_name, data.admin_key, data.photo
    )
    if success:
        return {"success": True, "message": "SuperAdmin registered successfully."}
    else:
        return {"success": False, "message": "Registration failed. Email may already exist."}