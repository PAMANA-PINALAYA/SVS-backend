from fastapi import APIRouter, HTTPException
import psycopg2
import os
from datetime import datetime

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