import psycopg2
import os
from fastapi import APIRouter, Query

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

@router.get("/admin/logs")
def get_logs(
    user_id: int = Query(None),
    user_type: str = Query("admin"),  # default to admin
    action_type: str = Query(None),
    name: str = Query(None)
):
    conn = get_db_conn()
    cur = conn.cursor()
    query = """
        SELECT
            l.id,
            l.user_id,
            l.user_type,
            l.role,
            l.action_type,
            l.description,
            l.related_id,
            l.created_at,
            l.user_name,
            l.user_photo
        FROM admin_responder_logs l
    """
    params = []
    conditions = ["l.user_type = 'admin'"]  # Only show admin logs in this endpoint
    if user_id:
        conditions.append("l.user_id = %s")
        params.append(user_id)
    if action_type:
        conditions.append("l.action_type = %s")
        params.append(action_type)
    if name:
        conditions.append("LOWER(l.user_name) LIKE %s")
        params.append(f"%{name.lower()}%")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY l.created_at DESC"
    cur.execute(query, tuple(params))
    logs = []
    for row in cur.fetchall():
        logs.append({
            "id": row[0],
            "admin_id": row[1],
            "user_type": row[2],
            "role": row[3],
            "action_type": row[4],
            "description": row[5],
            "related_id": row[6],
            "created_at": row[7].strftime("%Y-%m-%d %H:%M:%S") if row[7] else "",
            "full_name": row[8],
            "photo": row[9] or "policeman.png",
        })
    cur.close()
    conn.close()
    return {"logs": logs}