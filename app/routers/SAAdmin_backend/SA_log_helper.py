from fastapi import APIRouter, Query
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

@router.post("/superadmin/log_action")
def log_superadmin_action(
    user_id: int,
    action_type: str,
    description: str,
    related_id: int = None,
    user_name: str = None,
    user_photo: str = None
):
    role = "SuperAdmin"
    user_type = "superadmin"
    if not user_name:
        user_name = get_superadmin_name(user_id)
    if not user_photo:
        user_photo = "superadmin.png"
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO superadmin_logs (user_id, user_type, role, action_type, description, related_id, user_name, user_photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, user_type, role, action_type, description, related_id, user_name, user_photo))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.get("/superadmin/get_superadmin_name")
def get_superadmin_name(superadmin_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM superadmin_users WHERE id = %s", (superadmin_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else "Unknown SuperAdmin"

@router.get("/superadmin/logs")
def get_logs(
    user_id: int = Query(None),
    user_type: str = Query(None),
    role: str = Query(None),
    action_type: str = Query(None),
    name: str = Query(None),
    limit: int = Query(100)
):
    conn = get_db_conn()
    cursor = conn.cursor()
    query = """
        SELECT
            id,
            user_id,
            user_type,
            role,
            action_type,
            description,
            related_id,
            created_at,
            user_name,
            user_photo
        FROM superadmin_logs
    """
    params = []
    conditions = []
    if user_id:
        conditions.append("user_id = %s")
        params.append(user_id)
    if user_type:
        conditions.append("user_type = %s")
        params.append(user_type)
    if role:
        conditions.append("role = %s")
        params.append(role)
    if action_type:
        conditions.append("action_type = %s")
        params.append(action_type)
    if name:
        conditions.append("LOWER(user_name) LIKE %s")
        params.append(f"%{name.lower()}%")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += f" ORDER BY created_at DESC LIMIT {limit}"
    cursor.execute(query, tuple(params))
    logs = [
        {
            "id": row[0],
            "user_id": row[1],
            "user_type": row[2],
            "role": row[3],
            "action_type": row[4],
            "description": row[5],
            "related_id": row[6],
            "created_at": row[7].strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": row[8],
            "user_photo": row[9]
        }
        for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()
    return logs