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

@router.get("/alerts")
def get_alerts(
    status: str = Query("active", enum=["active", "logs"]),
    responder_id: int = Query(...)
):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        if status == "active":
            cursor.execute("""
                SELECT id, title, message, created_at, target_group, target_location, risk_level, status, action_status,
                       action_started_at, action_finished_at, action_duration, photo
                FROM admin_alert_pushing
                WHERE (action_status = 'no action' OR action_status = 'ongoing')
                  AND responder_id = %s
                ORDER BY created_at DESC
                LIMIT 30
            """, (responder_id,))
        else:
            cursor.execute("""
                SELECT id, title, message, created_at, target_group, target_location, risk_level, status, action_status,
                       action_started_at, action_finished_at, action_duration, photo
                FROM admin_alert_pushing
                WHERE action_status = 'finished'
                  AND responder_id = %s
                ORDER BY created_at DESC
                LIMIT 30
            """, (responder_id,))

        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "timestamp": row[3].isoformat() if row[3] else None,
                "target_group": row[4],
                "target_location": row[5],
                "risk_level": (row[6] or "low").lower(),
                "status": row[7],
                "action_status": row[8] if row[8] else "no action",
                "action_started_at": row[9].isoformat() if row[9] else None,
                "action_finished_at": row[10].isoformat() if row[10] else None,
                "action_duration": str(row[11]) if row[11] else None,
                "photo": row[17] if len(row) > 17 else None,
            })
        return {"alerts": alerts}
    finally:
        cursor.close()
        conn.close()