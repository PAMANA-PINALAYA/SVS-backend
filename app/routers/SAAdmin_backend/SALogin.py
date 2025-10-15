from fastapi import APIRouter, HTTPException
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

class LoginRequest(BaseModel):
    email: str
    password: str

@router.get("/superadmin/roles")
def get_superadmin_roles():
    # Return the roles you want to support
    return ["admin", "responder", "superadmin"]
    
@router.post("/superadmin/login")
def superadmin_login(data: LoginRequest):
    print("Login endpoint hit with:", data.email)
    try:
        hashed_pw = hashlib.sha256(data.password.encode("utf-8")).hexdigest()
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, full_name, photo FROM superadmin_users WHERE email=%s AND password=%s AND is_active=TRUE",
            (data.email, hashed_pw)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return {"success": True, "id": user[0], "full_name": user[1], "photo": user[2]}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials or inactive account.")
    except Exception as e:
        print("Login error:", e)
        raise HTTPException(status_code=500, detail="Internal server error")