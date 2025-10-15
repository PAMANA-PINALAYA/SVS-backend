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
def get_camera_alerts(camera_name: str = Query(None), limit: int = Query(10)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        if camera_name:
            cursor.execute("""
                SELECT camera_name, alert_type, description, timestamp
                FROM camera_alerts 
                WHERE camera_name = %s
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (camera_name, limit))
        else:
            cursor.execute("""
                SELECT camera_name, alert_type, description, timestamp
                FROM camera_alerts 
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (limit,))
        rows = cursor.fetchall()
        return [
            {
                "camera_name": row[0],
                "alert_type": row[1],
                "description": row[2],
                "timestamp": row[3].strftime("%Y-%m-%d %H:%M:%S") if row[3] else ""
            }
            for row in rows
        ]
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