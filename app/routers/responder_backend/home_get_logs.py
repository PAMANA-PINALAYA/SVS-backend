import psycopg2
import os
from fastapi import APIRouter, Query

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )

def log_action(user_id, user_type, role, action_type, description, related_id=None, user_name=None, user_photo=None):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO admin_responder_logs (user_id, user_type, role, action_type, description, related_id, user_name, user_photo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, user_type, role, action_type, description, related_id, user_name, user_photo))
    conn.commit()
    cursor.close()
    conn.close()

@router.get("/get_logs")
def get_logs(
    user_id: int = Query(None),
    user_type: str = Query(None),      # 'admin' or 'responder'
    role: str = Query(None),
    action_type: str = Query(None),    # for admin: action_type, for responder: log_type
    name: str = Query(None)
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
        FROM admin_responder_logs
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
    query += " ORDER BY created_at DESC LIMIT 100"
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
    return {"logs": logs}