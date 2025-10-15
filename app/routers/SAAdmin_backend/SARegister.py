from fastapi import APIRouter
from pydantic import BaseModel
import psycopg2
import hashlib
import os

router = APIRouter()

def get_db_conn():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    else:
        return psycopg2.connect(
            host="localhost",
            dbname="SmartSurveillanceSystem",
            user="postgres",
            password="123"
        )

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    admin_key: str
    photo: str = "policeman.png"

@router.post("/superadmin/register")
def superadmin_register(data: RegisterRequest):
    print("Register endpoint hit with:", data.email)
    if data.admin_key != "SUPER2024":
        return {"success": False, "message": "Invalid admin key."}
    try:
        hashed_pw = hashlib.sha256(data.password.encode("utf-8")).hexdigest()
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO superadmin_users (email, password, full_name, admin_key, photo) VALUES (%s, %s, %s, %s, %s)",
            (data.email, hashed_pw, data.full_name, data.admin_key, data.photo)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True, "message": "SuperAdmin registered successfully."}
    except Exception as e:
        print("Registration error:", e)
        return {"success": False, "message": "Registration failed. Email may already exist."}