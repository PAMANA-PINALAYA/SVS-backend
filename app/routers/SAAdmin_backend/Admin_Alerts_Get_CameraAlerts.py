from fastapi import APIRouter, HTTPException
from app.routers.SAAdmin_backend.Admin_Notification_get import add_admin_notification
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

@router.get("/admin/camera_alerts")
def get_camera_alerts():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, camera_name, alert_type, description, timestamp, city, barangay, street, exact_location,
                   brand, model, risk_level, is_read, from_latitude, from_longitude, photo
            FROM camera_alerts
            ORDER BY timestamp DESC
        """)
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                "id": row[0],
                "camera_name": row[1],
                "alert_type": row[2],
                "description": row[3],
                "timestamp": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else "",
                "city": row[5],
                "barangay": row[6],
                "street": row[7],
                "exact_location": row[8],
                "brand": row[9],
                "model": row[10],
                "risk_level": row[11],
                "is_read": row[12],
                "from_latitude": row[13],
                "from_longitude": row[14],
                "photo": row[15]
            })
        return alerts
    except Exception as e:
        print("Error in get_camera_alerts:", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/camera_alerts/add")
def add_camera_alert(camera_name: str, alert_type: str, description: str, risk_level: str, latitude: float = None, longitude: float = None, photo: str = None):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO camera_alerts (
                camera_name, alert_type, description, risk_level, timestamp,
                from_latitude, from_longitude, photo
            )
            VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s)
            RETURNING id
        """, (camera_name, alert_type, description, risk_level, latitude, longitude, photo))
        alert_id = cursor.fetchone()[0]
        conn.commit()
        add_admin_notification(
            title="Threat Detected",
            description=f"Threat '{alert_type}' detected on camera '{camera_name}': {description}",
            notif_type="threat",
            related_id=alert_id
        )
        return {"alert_id": alert_id}
    except Exception as e:
        conn.rollback()
        print("Error in add_camera_alert:", e)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/mark_alert_read")
def mark_alert_as_read(alert_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE camera_alerts SET is_read = TRUE WHERE id = %s", (alert_id,))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        print("Error in mark_alert_as_read:", e)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()