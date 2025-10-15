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

@router.get("/admin/system_logs")
def fetch_logs_from_db(log_type: str = Query(None), created_by: str = Query(None)):
    conn = get_db_conn()
    cur = conn.cursor()
    query = """
        SELECT id, log_type, related_id, description, started_at, finished_at, duration, created_by, created_at
        FROM system_logs
    """
    params = []
    conditions = []
    if log_type and log_type.strip():
        conditions.append("log_type = %s")
        params.append(log_type)
    if created_by and created_by.strip():
        if created_by.isdigit():
            conditions.append("(created_by = %s OR created_by = %s)")
            params.append(created_by)
            params.append(int(created_by))
        else:
            conditions.append("LOWER(created_by) LIKE %s")
            params.append(f"%{created_by.lower()}%")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC"
    cur.execute(query, tuple(params))
    logs = [
        {
            "id": row[0],
            "log_type": row[1],
            "related_id": row[2],
            "description": row[3],
            "started_at": row[4].isoformat() if row[4] else None,
            "finished_at": row[5].isoformat() if row[5] else None,
            "duration": str(row[6]) if row[6] else None,
            "created_by": row[7],
            "created_at": row[8].isoformat() if row[8] else None,
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return logs