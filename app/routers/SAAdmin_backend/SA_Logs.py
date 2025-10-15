from fastapi import APIRouter, Query
import psycopg2
import os

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )

@router.get("/admin/all_logs")
def fetch_all_logs(
    action_type: str = Query(None),
    name: str = Query(None),
    user_type: str = Query(None),
    order_by: str = Query("created_at"),
    order_dir: str = Query("DESC"),
    limit: int = Query(200)
):
    conn = get_db_conn()
    cur = conn.cursor()
    try:
        query = """
            SELECT
                l.user_name,
                l.role,
                l.user_type,
                l.description,
                l.created_at
            FROM admin_responder_logs l
            UNION ALL
            SELECT
                s.user_name,
                s.role,
                s.user_type,
                s.description,
                s.created_at
            FROM superadmin_logs s
        """
        params = []
        conditions = []
        if user_type:
            conditions.append("user_type = %s")
            params.append(user_type)
        if action_type:
            conditions.append("action_type = %s")
            params.append(action_type)
        if name:
            conditions.append("LOWER(user_name) LIKE %s")
            params.append(f"%{name.lower()}%")
        if conditions:
            query = f"SELECT * FROM ({query}) AS all_logs WHERE " + " AND ".join(conditions)
        query += f" ORDER BY created_at {order_dir} LIMIT %s"
        params.append(limit)
        cur.execute(query, tuple(params))
        logs = []
        for row in cur.fetchall():
            logs.append({
                "user_name": row[0],
                "role": row[1],
                "user_type": row[2],
                "description": row[3],
                "created_at": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else "",
            })
        return logs
    finally:
        cur.close()
        conn.close()