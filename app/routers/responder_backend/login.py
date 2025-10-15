from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
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

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@router.post("/login_responder")
async def login_responder(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JSONResponse(
            content={"success": False, "detail": "Username and password required"},
            status_code=400
        )

    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, full_name, username, password, is_active, approved, status, role
            FROM responders
            WHERE username = %s
        """, (username,))
        user = cursor.fetchone()

        if not user:
            return JSONResponse(
                content={"success": False, "detail": "Invalid username or password."},
                status_code=401
            )

        db_id, full_name, db_username, db_password, is_active, approved, status, role = user

        # Compare hashed password
        if db_password != hash_password(password):
            return JSONResponse(
                content={"success": False, "detail": "Invalid username or password."},
                status_code=401
            )

        status_clean = (status or "").strip().lower()

        if not (approved and is_active and status_clean == "approved"):
            return JSONResponse(
                content={"success": False, "detail": "Account not approved or inactive.", "status": status_clean},
                status_code=403
            )

        # Update last_login to NOW()
        cursor.execute("UPDATE responders SET last_login = NOW() WHERE id = %s", (db_id,))
        conn.commit()

        return JSONResponse(content={
            "success": True,
            "responder_id": db_id,
            "full_name": full_name,
            "username": db_username,
            "role": role,
            "status": "approved"
        })

    finally:
        cursor.close()
        conn.close()