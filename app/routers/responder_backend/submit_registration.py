from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import psycopg2
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.routers.SAAdmin_backend.Admin_Notification_get import add_admin_notification
import hashlib
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


DEFAULT_PROFILE_IMAGE = "profile.png"
DB_HOST = "localhost"
DB_NAME = "SmartSurveillanceSystem"
DB_USER = "postgres"
DB_PASS = "123"

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

class RegistrationModel(BaseModel):
    full_name: str
    email: str
    phone: str
    username: str
    password: str
    role: str = "Responder"
    address: str = ""
    assigned_at: str = "malabon"

@router.post("/submit_registration")
def submit_registration(data: RegistrationModel):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM pending_responders WHERE email = %s OR username = %s",
            (data.email, data.username)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email or username already exists (pending).")
        cursor.execute(
            "SELECT id FROM responders WHERE email = %s OR username = %s",
            (data.email, data.username)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email or username already exists (active).")
        cursor.execute(
            """INSERT INTO pending_responders 
            (full_name, email, phone, username, password, role, address, assigned_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id""",
            (
                data.full_name,
                data.email,
                data.phone,
                data.username,
                hash_password(data.password),
                data.role,
                data.address,
                data.assigned_at
            )
        )
        pending_id = cursor.fetchone()[0]
        conn.commit()
        # Optionally notify admin here
        return {
            "success": True,
            "message": "Registration submitted successfully. Your account is pending admin approval."
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()