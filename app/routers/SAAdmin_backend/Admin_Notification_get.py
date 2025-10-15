from fastapi import APIRouter, HTTPException
import psycopg2
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

@router.get("/admin/notifications")
def get_admin_notifications():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, title, description, created_at, is_read, type, related_id
            FROM admin_notifications
            ORDER BY created_at DESC
            LIMIT 50
        """)
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "created_at": row[3].strftime("%Y-%m-%d %H:%M:%S"),
                "is_read": row[4],
                "type": row[5],
                "related_id": row[6]
            })
        return notifications
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/notifications/mark_read")
def mark_notification_read(notification_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE admin_notifications SET is_read = TRUE WHERE id = %s", (notification_id,))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/notifications/add")
def add_admin_notification(title: str, description: str, notif_type: str, related_id: int = None):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO admin_notifications (title, description, type, related_id) VALUES (%s, %s, %s, %s)",
            (title, description, notif_type, related_id)
        )
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()