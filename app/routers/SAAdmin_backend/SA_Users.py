from fastapi import APIRouter, HTTPException, Query, Body
import psycopg2
import os
from datetime import datetime
from app.routers.SAAdmin_backend.SA_log_helper import log_superadmin_action
from app.routers.SAAdmin_backend.db_connection import db_manager
import hashlib

router = APIRouter()

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )

@router.get("/superadmin/users")
def fetch_all_users():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        query = """
            SELECT id, full_name, email, phone, role, is_active, created_at, 'admin' as user_type,
                   NULL AS approved, NULL AS status, last_login, NULL AS assigned_at, NULL AS username, last_logout
            FROM admin_users
            UNION ALL
            SELECT id, full_name, email, phone, role, is_active, created_at, 'responder' as user_type,
                   approved, status, last_login, assigned_at, username, last_logout
            FROM responders
        """
        cursor.execute(query)
        users = cursor.fetchall()
        return [
            {
                "id": row[0],
                "full_name": row[1],
                "email": row[2],
                "phone": row[3],
                "role": row[4],
                "is_active": row[5],
                "created_at": row[6].strftime("%Y-%m-%d %H:%M:%S") if row[6] else "",
                "user_type": row[7],
                "approved": row[8],
                "status": row[9],
                "last_login": row[10].strftime("%Y-%m-%d %H:%M:%S") if row[10] else "",
                "assigned_at": row[11],
                "username": row[12],
                "last_logout": row[13].strftime("%Y-%m-%d %H:%M:%S") if row[13] else ""
            }
            for row in users
        ]
    finally:
        cursor.close()
        conn.close()

@router.get("/superadmin/pending_requests")
def fetch_pending_requests():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, full_name, email, phone, role, created_at, address, assigned_at
            FROM pending_responders
        """)
        pending_responders = cursor.fetchall()
        return [
            {
                "id": row[0],
                "full_name": row[1],
                "email": row[2],
                "phone": row[3],
                "role": row[4],
                "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else "",
                "address": row[6],
                "assigned_at": row[7]
            }
            for row in pending_responders
        ]
    finally:
        cursor.close()
        conn.close()

@router.get("/superadmin/user_counts")
def count_users():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM admin_users")
        admin_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM responders")
        responder_count = cursor.fetchone()[0]
        return {"admin_count": admin_count, "responder_count": responder_count}
    finally:
        cursor.close()
        conn.close()

@router.post("/superadmin/user/add")
def add_user(data: dict = Body(...), superadmin_id: int = Query(None)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        if data["role"].lower() == "responder":
            if not data.get("username") or not data.get("username").strip():
                raise HTTPException(status_code=400, detail="Username is required for responders.")
            if not data.get("password") or not data.get("password").strip():
                raise HTTPException(status_code=400, detail="Password is required for responders.")
            cursor.execute("SELECT 1 FROM responders WHERE username=%s OR email=%s", (data["username"], data["email"]))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Username or email already exists.")
            hashed_password = hash_password(data["password"])
            cursor.execute("""
                INSERT INTO responders (
                    full_name, email, phone, username, password, role, created_at, is_active, photo, address, assigned_at, approved, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data["full_name"], data["email"], data.get("phone"), data["username"], hashed_password,
                "Responder", datetime.now(), True, data.get("photo", "profile.png"),
                data.get("address", ""), data.get("assigned_at", "malabon"),
                True, "approved"
            ))
            if superadmin_id:
                log_superadmin_action(superadmin_id, "add_responder", f"Added responder: {data['full_name']}")
        elif data["role"].lower() == "admin":
            if not data.get("email") or not data.get("email").strip():
                raise HTTPException(status_code=400, detail="Email is required for admins.")
            if not data.get("password") or not data.get("password").strip():
                raise HTTPException(status_code=400, detail="Password is required for admins.")
            hashed_password = hash_password(data["password"])
            cursor.execute("""
                INSERT INTO admin_users (email, password, full_name, photo, created_at, is_active, role, phone)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data["email"], hashed_password, data["full_name"], data.get("photo", "policeman.png"),
                datetime.now(), True, "admin", data.get("phone")
            ))
            if superadmin_id:
                log_superadmin_action(superadmin_id, "add_admin", f"Added admin: {data['full_name']}")
        else:
            raise HTTPException(status_code=400, detail="Invalid role.")
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.put("/superadmin/user/update/{user_id}")
def update_user(user_id: int, data: dict = Body(...), role: str = Query(...), superadmin_id: int = Query(None)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        table = "admin_users" if role.lower() == "admin" else "responders"
        fields = []
        params = []
        for k in ["full_name", "email", "phone"]:
            if k in data:
                fields.append(f"{k}=%s")
                params.append(data[k])
        if "password" in data and data["password"]:
            fields.append("password=%s")
            params.append(db_manager.hash_password(data["password"]))
        if role.lower() == "responder":
            if "approved" in data:
                fields.append("approved=%s")
                params.append(data["approved"])
            if "status" in data:
                fields.append("status=%s")
                params.append(data["status"])
            if "username" in data and data["username"]:
                fields.append("username=%s")
                params.append(data["username"])
            if "assigned_at" in data and data["assigned_at"]:
                fields.append("assigned_at=%s")
                params.append(data["assigned_at"])
        params.append(user_id)
        if fields:
            cursor.execute(f"UPDATE {table} SET {', '.join(fields)} WHERE id=%s", tuple(params))
            if superadmin_id:
                log_superadmin_action(superadmin_id, "edit_user", f"Edited {role}: {data.get('full_name', user_id)}", related_id=user_id)
            conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.delete("/superadmin/user/delete/{user_id}")
def delete_user(user_id: int, role: str = Query(...), superadmin_id: int = Query(None)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        table = "admin_users" if role.lower() == "admin" else "responders"
        cursor.execute(f"DELETE FROM {table} WHERE id = %s", (user_id,))
        log_superadmin_action(superadmin_id, "delete_user", f"Deleted {role}: {user_id}", related_id=user_id)
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.put("/superadmin/user/set_active/{user_id}")
def set_user_active(user_id: int, is_active: bool, role: str = Query(...), superadmin_id: int = Query(None)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        table = "admin_users" if role.lower() == "admin" else "responders"
        cursor.execute(f"UPDATE {table} SET is_active = %s WHERE id = %s", (is_active, user_id))
        action = "unblock_user" if is_active else "suspend_user"
        log_superadmin_action(superadmin_id, action, f"{'Unblocked' if is_active else 'Suspended'} {role}: {user_id}", related_id=user_id)
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.post("/superadmin/pending_responder/approve/{pending_id}")
def approve_pending_responder(pending_id: int, superadmin_id: int = Query(None)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT full_name, email, phone, username, password, role, address, assigned_at, created_at
            FROM pending_responders WHERE id = %s
        """, (pending_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Pending responder not found.")
        cursor.execute("""
            INSERT INTO responders (
                full_name, email, phone, username, password, role, created_at,
                is_active, photo, address, assigned_at, approved, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row[0], row[1], row[2], row[3], row[4], row[5], row[8],
            True, "profile.png", row[6], row[7], True, "approved"
        ))
        cursor.execute("DELETE FROM pending_responders WHERE id = %s", (pending_id,))
        if superadmin_id:
            log_superadmin_action(superadmin_id, "approve_user", f"Approved responder: {row[3]}", related_id=pending_id)
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.delete("/superadmin/pending_responder/reject/{pending_id}")
def reject_pending_responder(pending_id: int, superadmin_id: int = Query(None)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM pending_responders WHERE id = %s", (pending_id,))
        if superadmin_id:
            log_superadmin_action(superadmin_id, "reject_user", f"Rejected pending responder: {pending_id}", related_id=pending_id)
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.put("/superadmin/responder/assign_location/{responder_id}")
def assign_responder_location(responder_id: int, street_name: str, superadmin_id: int = Query(None)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE responders SET assigned_at = %s WHERE id = %s", (street_name, responder_id))
        log_superadmin_action(superadmin_id, "assign_location", f"Assigned responder {responder_id} to {street_name}", related_id=responder_id)
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.get("/superadmin/pending_admins")
def fetch_pending_admins():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, full_name, email, phone, created_at, photo
            FROM pending_admins
        """)
        return [
            {
                "id": row[0],
                "full_name": row[1],
                "email": row[2],
                "phone": row[3],
                "created_at": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else "",
                "photo": row[5]
            }
            for row in cursor.fetchall()
        ]
    finally:
        cursor.close()
        conn.close()

@router.post("/superadmin/pending_admin/approve/{pending_id}")
def approve_pending_admin(pending_id: int, superadmin_id: int = Query(None)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT full_name, email, phone, password, photo, created_at
            FROM pending_admins WHERE id = %s
        """, (pending_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Pending admin not found.")
        cursor.execute("""
            INSERT INTO admin_users (
                email, password, full_name, photo, created_at, is_active, role, phone
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row[1], row[3], row[0], row[4], row[5], True, "admin", row[2]
        ))
        cursor.execute("DELETE FROM pending_admins WHERE id = %s", (pending_id,))
        if superadmin_id:
            log_superadmin_action(superadmin_id, "approve_admin", f"Approved admin: {row[1]}", related_id=pending_id)
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.delete("/superadmin/pending_admin/reject/{pending_id}")
def reject_pending_admin(pending_id: int, superadmin_id: int = Query(None)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM pending_admins WHERE id = %s", (pending_id,))
        if superadmin_id:
            log_superadmin_action(superadmin_id, "reject_admin", f"Rejected pending admin: {pending_id}", related_id=pending_id)
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.get("/superadmin/roles")
def get_roles():
    return ["admin", "Responder"]