from fastapi import APIRouter, HTTPException
from app.routers.SAAdmin_backend.Admin_Notification_get import add_admin_notification
import psycopg2

router = APIRouter()

@router.get("/admin/camera_alerts")
def get_camera_alerts():
    conn = psycopg2.connect(
        host="localhost",
        dbname="SmartSurveillanceSystem",
        user="postgres",
        password="123"
    )
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, camera_name, alert_type, description, risk_level, timestamp, from_latitude, from_longitude, photo, is_read FROM camera_alerts ORDER BY timestamp DESC"
        )
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                "id": row[0],
                "camera_name": row[1],
                "alert_type": row[2],
                "description": row[3],
                "risk_level": row[4],
                "timestamp": str(row[5]),
                "latitude": row[6],
                "longitude": row[7],
                "photo": row[8],
                "is_read": row[9]
            })
        return alerts
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/camera_alerts/add")
def add_camera_alert(camera_name: str, alert_type: str, description: str, risk_level: str, latitude: float = None, longitude: float = None, photo: str = None):
    conn = psycopg2.connect(
        host="localhost",
        dbname="SmartSurveillanceSystem",
        user="postgres",
        password="123"
    )
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
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/mark_alert_read")
def mark_alert_as_read(alert_id: int):
    conn = psycopg2.connect(
        host="localhost",
        dbname="SmartSurveillanceSystem",
        user="postgres",
        password="123"
    )
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE camera_alerts SET is_read = TRUE WHERE id = %s", (alert_id,))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()