from fastapi import APIRouter, HTTPException
import psycopg2
import os
from datetime import datetime, timedelta

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )

@router.get("/admin/dashboard/overview")
def dashboard_overview():
    overview = {}
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM cctv_cameras")
        total_cameras = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM microphones")
        total_mics = cursor.fetchone()[0]
        overview["total_devices"] = total_cameras + total_mics

        cursor.execute("SELECT COUNT(*) FROM responders_report WHERE status != 'Approved'")
        overview["total_unapproved_reports"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM responders WHERE approved = false")
        overview["responders_pending"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM responders WHERE is_active = true")
        overview["responders_active"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM responders WHERE is_active = false")
        overview["responders_deactivated"] = cursor.fetchone()[0]

        try:
            from ultralytics import YOLO
            model = YOLO("yolov8n.pt")
            overview["model_name"] = getattr(model, "model", None).__class__.__name__ if hasattr(model, "model") else "YOLOv8n"
        except Exception:
            overview["model_name"] = "YOLOv8n"

        try:
            cursor.execute("SELECT COUNT(*) FROM camera_alerts WHERE is_read = FALSE")
            overview["total_pending_alerts"] = cursor.fetchone()[0]
        except Exception:
            cursor.execute("SELECT COUNT(*) FROM camera_alerts")
            overview["total_pending_alerts"] = cursor.fetchone()[0]

        return overview
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/dashboard/device_locations")
def all_device_locations():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT name, latitude, longitude, 'Camera' as type, id FROM cctv_cameras WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            UNION ALL
            SELECT name, latitude, longitude, 'Microphone' as type, id FROM microphones WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        rows = cursor.fetchall()
        return [
            {
                "name": row[0],
                "latitude": row[1],
                "longitude": row[2],
                "type": row[3],
                "id": row[4]
            }
            for row in rows
        ]
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/dashboard/threat_heatmap")
def threat_heatmap():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                COALESCE(camera_alerts.camera_name, camera_alerts.exact_location, 'Unknown') as device_name,
                COUNT(*) as threat_count,
                MAX(camera_alerts."timestamp") as last_alert
            FROM camera_alerts
            WHERE camera_alerts."timestamp" > NOW() - INTERVAL '5 minutes'
            GROUP BY device_name
            ORDER BY threat_count DESC, last_alert DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        return [
            {
                "device_name": row[0],
                "threat_count": row[1],
                "last_alert": row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else ""
            }
            for row in rows
        ]
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/dashboard/recent_camera_alerts")
def recent_camera_alerts():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                ca.camera_name, 
                ca.alert_type, 
                ca.description, 
                ca.risk_level, 
                ca."timestamp", 
                ca.from_latitude, 
                ca.from_longitude,
                cc.latitude as camera_lat,
                cc.longitude as camera_lon,
                cc.exact_location as camera_location,
                CONCAT(cc.city, ', ', cc.barangay, ', ', cc.street) as camera_zone
            FROM camera_alerts ca
            LEFT JOIN cctv_cameras cc ON ca.camera_name = cc.name
            WHERE ca."timestamp" > NOW() - INTERVAL '2 minutes'
            ORDER BY ca."timestamp" DESC
        """)
        rows = cursor.fetchall()
        alerts = []
        for row in rows:
            camera_name, alert_type, description, risk_level, timestamp, from_lat, from_lon, camera_lat, camera_lon, camera_location, camera_zone = row
            final_lat = from_lat if from_lat is not None else camera_lat
            final_lon = from_lon if from_lon is not None else camera_lon
            if final_lat is not None and final_lon is not None:
                alerts.append({
                    "camera_name": camera_name,
                    "alert_type": alert_type,
                    "description": description,
                    "risk_level": risk_level,
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "",
                    "latitude": float(final_lat),
                    "longitude": float(final_lon),
                    "location": camera_location or "Unknown Location",
                    "zone": camera_zone or "Unknown Zone"
                })
        return alerts
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/dashboard/active_threats")
def active_threats():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                ca.camera_name,
                ca.alert_type,
                ca.risk_level,
                ca."timestamp",
                COALESCE(ca.from_latitude, cc.latitude) as latitude,
                COALESCE(ca.from_longitude, cc.longitude) as longitude,
                cc.exact_location,
                CONCAT(cc.city, ', ', cc.barangay, ', ', cc.street) as zone
            FROM camera_alerts ca
            LEFT JOIN cctv_cameras cc ON ca.camera_name = cc.name
            WHERE ca."timestamp" > NOW() - INTERVAL '30 seconds'
            AND COALESCE(ca.from_latitude, cc.latitude) IS NOT NULL
            AND COALESCE(ca.from_longitude, cc.longitude) IS NOT NULL
            ORDER BY ca."timestamp" DESC
        """)
        rows = cursor.fetchall()
        return [
            {
                "camera_name": row[0],
                "alert_type": row[1],
                "risk_level": row[2],
                "timestamp": row[3].strftime("%Y-%m-%d %H:%M:%S") if row[3] else "",
                "latitude": float(row[4]),
                "longitude": float(row[5]),
                "location": row[6] or "Unknown",
                "zone": row[7] or "Unknown"
            }
            for row in rows
        ]
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/dashboard/check_new_threats")
def check_new_threats(last_check_time: str = None):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        if last_check_time is None:
            last_check_time = (datetime.now() - timedelta(seconds=30)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM camera_alerts ca
            LEFT JOIN cctv_cameras cc ON ca.camera_name = cc.name
            WHERE ca."timestamp" > %s
            AND COALESCE(ca.from_latitude, cc.latitude) IS NOT NULL
            AND COALESCE(ca.from_longitude, cc.longitude) IS NOT NULL
        """, (last_check_time,))
        count = cursor.fetchone()[0]
        return {"new_threats": count > 0}
    finally:
        cursor.close()
        conn.close()