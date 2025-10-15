from fastapi import APIRouter, HTTPException
import psycopg2
import os
from app.routers.SAAdmin_backend.admin_log_helper import log_action

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

@router.get("/admin/locations")
def get_locations():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT assigned_at FROM responders")
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/responders")
def get_responders():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, full_name, assigned_at FROM responders")
        return [{"id": row[0], "full_name": row[1], "assigned_at": row[2]} for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/push_alert")
def push_alert(
    title: str,
    message: str,
    created_by: int,
    target_group: str,
    risk_level: str,
    target_location: str = None,
    assigned_responder: int = None,
    photo: str = None
):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT full_name FROM admin_users WHERE id = %s", (created_by,))
        admin_row = cursor.fetchone()
        created_by_name = admin_row[0] if admin_row else None
        if created_by is not None:
            log_action(created_by, "Push Alert", f"Pushed alert '{title}' to group '{target_group}'", None, created_by_name)
        responder_ids = []
        if target_group == "all":
            cursor.execute("SELECT id FROM responders")
            responder_ids = [row[0] for row in cursor.fetchall()]
        elif target_group == "location" and target_location:
            cursor.execute("SELECT id FROM responders WHERE assigned_at = %s", (target_location,))
            responder_ids = [row[0] for row in cursor.fetchall()]
        elif target_group == "individual" and assigned_responder:
            responder_ids = [assigned_responder]
        if not responder_ids:
            raise HTTPException(status_code=404, detail="No responders found for the selected group/location.")
        for rid in responder_ids:
            cursor.execute("""
                INSERT INTO admin_alert_pushing 
                    (title, message, created_by, created_by_name, target_group, target_location, assigned_responder, responder_id, risk_level, photo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (title, message, created_by, created_by_name, target_group, target_location, rid if target_group == "individual" else None, rid, risk_level, photo))
        conn.commit()
        log_action(created_by, "Push Alert", f"Pushed alert '{title}' to group '{target_group}'", None, created_by_name)
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()