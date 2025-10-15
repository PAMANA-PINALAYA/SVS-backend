from fastapi import APIRouter, HTTPException, Query
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
def add_camera_alert(camera_name: str, alert_type: str, description: str):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO camera_alerts (camera_name, alert_type, description, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (camera_name, alert_type, description, datetime.now()))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()