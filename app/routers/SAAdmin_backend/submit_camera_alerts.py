from fastapi import APIRouter, HTTPException
import psycopg2
import os
from datetime import datetime

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )

@router.post("/superadmin/camera_alerts/submit")
def submit_camera_alert(cam_data: list, alert_type: str, description: str, risk_level: str):
    name = cam_data[0]
    city = cam_data[3]
    barangay = cam_data[4]
    street = cam_data[5]
    exact_location = cam_data[6]
    brand = cam_data[17]
    model = cam_data[18]
    timestamp = datetime.now()

    conn = get_db_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO camera_alerts (
                camera_name, alert_type, description, timestamp,
                city, barangay, street, exact_location, brand, model, risk_level
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name, alert_type, description, timestamp,
            city, barangay, street, exact_location, brand, model, risk_level
        ))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error submitting camera alert: {e}")
    finally:
        cur.close()
        conn.close()