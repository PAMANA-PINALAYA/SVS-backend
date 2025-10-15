from fastapi import APIRouter, Query, HTTPException
from fastapi import Body
from pydantic import BaseModel
from app.routers.responder_backend.config import get_db_conn

router = APIRouter()

class ResponderIdModel(BaseModel):
    responder_id: int

@router.get("/get_notifications")
def get_notifications(responder_id: int = Query(...)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, title, message, notif_type, is_read, created_at
            FROM responder_notifications
            WHERE responder_id = %s AND cleared = FALSE
            ORDER BY created_at DESC
            LIMIT 100
        """, (responder_id,))
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                "id": row[0],
                "title": row[1],
                "message": row[2],
                "type": row[3],
                "is_read": row[4],
                "created_at": row[5].strftime("%Y-%m-%d %H:%M"),
            })
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/get_cleared_notifications")
def get_cleared_notifications(responder_id: int = Query(...)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, title, message, notif_type, is_read, created_at
            FROM responder_notifications
            WHERE responder_id = %s AND cleared = TRUE
            ORDER BY created_at DESC
            LIMIT 100
        """, (responder_id,))
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                "id": row[0],
                "title": row[1],
                "message": row[2],
                "type": row[3],
                "is_read": row[4],
                "created_at": row[5].strftime("%Y-%m-%d %H:%M"),
            })
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/mark_all_notifications_read")
def mark_all_notifications_read(data: ResponderIdModel):
    responder_id = data.responder_id
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE responder_notifications SET is_read = TRUE WHERE responder_id = %s AND cleared = FALSE",
            (responder_id,)
        )
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.post("/clear_notifications")
def clear_notifications(data: ResponderIdModel):
    responder_id = data.responder_id
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE responder_notifications SET cleared = TRUE WHERE responder_id = %s AND cleared = FALSE",
            (responder_id,)
        )
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

class NotificationIdModel(BaseModel):
    notification_id: int

@router.post("/mark_notification_read")
def mark_notification_read(data: NotificationIdModel):
    notification_id = data.notification_id
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE responder_notifications SET is_read = TRUE WHERE id = %s",
            (notification_id,)
        )
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()