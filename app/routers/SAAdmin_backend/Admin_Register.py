from fastapi import APIRouter, HTTPException
import psycopg2
import os
from app.routers.SAAdmin_backend.db_connection import db_manager

router = APIRouter()

@router.post("/admin/register")
def admin_register(email: str, password: str, full_name: str, photo: str = "policeman.png", phone: str = None):
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM pending_admins WHERE email = %s", (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Registration failed. Email is already pending approval.")
        cursor.execute("SELECT id FROM admin_users WHERE email = %s", (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Registration failed. Email already exists.")
        hashed_password = db_manager.hash_password(password)
        cursor.execute(""" 
            INSERT INTO pending_admins (full_name, email, phone, password, photo)
            VALUES (%s, %s, %s, %s, %s)
        """, (full_name, email, phone, hashed_password, photo))
        conn.commit()
        return {"success": True, "message": "Registration submitted. Awaiting superadmin approval."}
    finally:
        cursor.close()
        conn.close()