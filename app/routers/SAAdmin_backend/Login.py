# filepath: [Login.py](http://_vscodecontentref_/0)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.routers.SAAdmin_backend.db_connection import db_manager

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/admin/login")
def admin_login(data: LoginRequest):
    result = db_manager.verify_admin_login(data.email, data.password)
    if result:
        admin_id = result[0]
        return {"success": True, "id": admin_id, "full_name": result[1], "photo": result[2]}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials or inactive account.")