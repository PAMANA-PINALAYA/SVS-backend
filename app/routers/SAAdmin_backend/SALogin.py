# filepath: [SALogin.py](http://_vscodecontentref_/1)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.routers.SAAdmin_backend.db_connection import db_manager

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/superadmin/login")
def superadmin_login(data: LoginRequest):
    print("Login endpoint hit with:", data.email)
    result = db_manager.verify_superadmin_login(data.email, data.password)
    if result:
        return {"success": True, "id": result[0], "full_name": result[1], "photo": result[2]}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials or inactive account.")