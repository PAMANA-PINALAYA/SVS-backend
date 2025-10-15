from fastapi import APIRouter, HTTPException
import psycopg2
import os
from app.routers.SAAdmin_backend.Admin_Notification_get import add_admin_notification

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )

@router.post("/superadmin/emergency_contact/add")
def add_emergency_contact(name: str, phone: str, role: str, address: str, is_active: bool = True):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO emergency_contacts (name, phone, role, address, is_active) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (name, phone, role, address, is_active)
        )
        contact_id = cursor.fetchone()[0]
        conn.commit()
        add_admin_notification(
            title="New Emergency Contact",
            description=f"Emergency contact '{name}' was added.",
            notif_type="emergency",
            related_id=contact_id
        )
        return {"contact_id": contact_id}
    finally:
        cursor.close()
        conn.close()

@router.get("/superadmin/emergency_contacts")
def get_emergency_contacts():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, phone, role, address, is_active, created_by, created_at, updated_at
            FROM emergency_contacts
            ORDER BY created_at DESC
        """)
        contacts = cursor.fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "phone": row[2],
                "role": row[3],
                "address": row[4],
                "is_active": row[5],
                "created_by": row[6],
                "created_at": str(row[7]),
                "updated_at": str(row[8])
            }
            for row in contacts
        ]
    finally:
        cursor.close()
        conn.close()

@router.post("/superadmin/emergency_contact/post")
def post_emergency_contact(name: str, phone: str, role: str, address: str, created_by: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO emergency_contacts (name, phone, role, address, created_by)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (name, phone, role, address, created_by))
        contact_id = cursor.fetchone()[0]
        conn.commit()
        add_admin_notification(
            title="New Emergency Contact",
            description=f"Emergency contact '{name}' was added.",
            notif_type="emergency",
            related_id=contact_id
        )
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/superadmin/emergency_contact/edit")
def edit_emergency_contact(contact_id: int, name: str, phone: str, role: str, address: str, is_active: bool):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE emergency_contacts
            SET name=%s, phone=%s, role=%s, address=%s, is_active=%s, updated_at=NOW()
            WHERE id=%s
        """, (name, phone, role, address, is_active, contact_id))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.delete("/superadmin/emergency_contact/delete")
def delete_emergency_contact(contact_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM emergency_contacts WHERE id=%s", (contact_id,))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()