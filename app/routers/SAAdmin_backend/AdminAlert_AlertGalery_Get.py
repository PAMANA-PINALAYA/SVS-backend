from fastapi import APIRouter, HTTPException
import os
import psycopg2

router = APIRouter()

@router.get("/admin/gallery/images")
def get_gallery_images():
    detected_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "Detected_Footages"
        )
    )
    if not os.path.exists(detected_dir):
        return []
    return [f for f in os.listdir(detected_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

@router.get("/admin/gallery/alert_by_photo")
def get_alert_by_photo(photo_filename: str):
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, camera_name, alert_type, description, risk_level, timestamp, city, barangay, street, exact_location, brand, model, from_latitude, from_longitude, photo
            FROM camera_alerts
            WHERE photo = %s
            LIMIT 1
        """, (photo_filename,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "camera_name": row[1],
                "alert_type": row[2],
                "description": row[3],
                "risk_level": row[4],
                "timestamp": str(row[5]),
                "city": row[6],
                "barangay": row[7],
                "street": row[8],
                "exact_location": row[9],
                "brand": row[10],
                "model": row[11],
                "from_latitude": row[12],
                "from_longitude": row[13],
                "photo": row[14],
            }
        return None
    finally:
        cursor.close()
        conn.close()