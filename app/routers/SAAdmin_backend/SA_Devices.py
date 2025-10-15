from fastapi import APIRouter, HTTPException
import psycopg2
import os
from app.routers.SAAdmin_backend.Admin_Notification_get import add_admin_notification

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )

@router.get("/superadmin/cameras")
def get_cameras():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, type, url, city, barangay, street, exact_location,
                   ai_supported, mic_supported, night_vision, status, resolution, frame_rate,
                   poe_powered, dc_powered, storage_supported, field_of_view, brand, model,
                   latitude, longitude
            FROM cctv_cameras ORDER BY id DESC
        """)
        cameras = []
        for row in cursor.fetchall():
            cameras.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "url": row[3],
                "city": row[4],
                "barangay": row[5],
                "street": row[6],
                "exact_location": row[7],
                "ai_supported": row[8],
                "mic_supported": row[9],
                "night_vision": row[10],
                "status": row[11],
                "resolution": row[12],
                "frame_rate": row[13],
                "poe_powered": row[14],
                "dc_powered": row[15],
                "storage_supported": row[16],
                "field_of_view": row[17],
                "brand": row[18],
                "model": row[19],
                "latitude": row[20],
                "longitude": row[21]
            })
        return cameras
    finally:
        cursor.close()
        conn.close()

@router.post("/superadmin/camera/add")
def add_camera(data: dict):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO cctv_cameras
            (name, type, url, city, barangay, street, exact_location,
             ai_supported, mic_supported, night_vision, status, resolution, frame_rate,
             poe_powered, dc_powered, storage_supported, field_of_view, brand, model,
             latitude, longitude, superadmin_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["name"], data["type"], data["url"], data["city"], data["barangay"], data["street"], data["exact_location"],
            data["ai_supported"], data["mic_supported"], data["night_vision"], data["status"], data["resolution"], data["frame_rate"],
            data["poe_powered"], data["dc_powered"], data["storage_supported"], data["field_of_view"], data["brand"], data["model"],
            data.get("latitude"), data.get("longitude"), data.get("superadmin_id")
        ))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.get("/superadmin/microphones")
def get_microphones():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, type, city, barangay, street, exact_location,
                   ai_supported, noise_reduction, sensitivity_db, poe_powered, dc_powered,
                   esp32_version, mic_model, status, latitude, longitude
            FROM microphones ORDER BY id DESC
        """)
        mics = cursor.fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "city": row[3],
                "barangay": row[4],
                "street": row[5],
                "exact_location": row[6],
                "ai_supported": row[7],
                "noise_reduction": row[8],
                "sensitivity_db": row[9],
                "poe_powered": row[10],
                "dc_powered": row[11],
                "esp32_version": row[12],
                "mic_model": row[13],
                "status": row[14],
                "latitude": row[15],
                "longitude": row[16]
            }
            for row in mics
        ]
    finally:
        cursor.close()
        conn.close()

@router.post("/superadmin/microphone/add")
def add_microphone(data: dict):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO microphones (name, type, city, barangay, street, exact_location,
                ai_supported, noise_reduction, sensitivity_db, poe_powered, dc_powered,
                esp32_version, mic_model, status, latitude, longitude, superadmin_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data["name"], data["type"], data["city"], data["barangay"], data["street"], data["exact_location"],
            data["ai_supported"], data["noise_reduction"], data["sensitivity_db"], data["poe_powered"], data["dc_powered"],
            data["esp32_version"], data["mic_model"], data["status"], data.get("latitude"), data.get("longitude"), data.get("superadmin_id")
        ))
        mic_id = cursor.fetchone()[0]
        conn.commit()
        add_admin_notification(
            title="New Microphone Added",
            description=f"Microphone '{data['name']}' was added by Super Admin.",
            notif_type="device",
            related_id=mic_id
        )
        return {"mic_id": mic_id}
    finally:
        cursor.close()
        conn.close()

@router.put("/superadmin/camera/update/{camera_id}")
def update_camera(camera_id: int, data: dict):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE cctv_cameras SET
                name=%s, type=%s, url=%s, city=%s, barangay=%s, street=%s, exact_location=%s,
                ai_supported=%s, mic_supported=%s, night_vision=%s, status=%s, resolution=%s, frame_rate=%s,
                poe_powered=%s, dc_powered=%s, storage_supported=%s, field_of_view=%s, brand=%s, model=%s,
                latitude=%s, longitude=%s
            WHERE id=%s
        """, (
            data["name"], data["type"], data["url"], data["city"], data["barangay"], data["street"], data["exact_location"],
            data["ai_supported"], data["mic_supported"], data["night_vision"], data["status"], data["resolution"], data["frame_rate"],
            data["poe_powered"], data["dc_powered"], data["storage_supported"], data["field_of_view"], data["brand"], data["model"],
            data.get("latitude"), data.get("longitude"), camera_id
        ))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.delete("/superadmin/camera/delete/{camera_id}")
def delete_camera(camera_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cctv_cameras WHERE id=%s", (camera_id,))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.put("/superadmin/camera/reassign/{camera_id}")
def reassign_camera(camera_id: int, new_barangay: str = None, new_latitude: float = None, new_longitude: float = None):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE cctv_cameras SET barangay=%s, latitude=%s, longitude=%s WHERE id=%s
        """, (new_barangay, new_latitude, new_longitude, camera_id))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.put("/superadmin/microphone/update/{mic_id}")
def update_microphone(mic_id: int, data: dict):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE microphones SET
                name=%s, type=%s, city=%s, barangay=%s, street=%s, exact_location=%s,
                ai_supported=%s, noise_reduction=%s, sensitivity_db=%s, poe_powered=%s, dc_powered=%s,
                esp32_version=%s, mic_model=%s, status=%s, latitude=%s, longitude=%s
            WHERE id=%s
        """, (
            data["name"], data["type"], data["city"], data["barangay"], data["street"], data["exact_location"],
            data["ai_supported"], data["noise_reduction"], data["sensitivity_db"], data["poe_powered"], data["dc_powered"],
            data["esp32_version"], data["mic_model"], data["status"], data.get("latitude"), data.get("longitude"), mic_id
        ))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.delete("/superadmin/microphone/delete/{mic_id}")
def delete_microphone(mic_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM microphones WHERE id=%s", (mic_id,))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.put("/superadmin/microphone/reassign/{mic_id}")
def reassign_microphone(mic_id: int, new_barangay: str = None, new_latitude: float = None, new_longitude: float = None):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE microphones SET barangay=%s, latitude=%s, longitude=%s WHERE id=%s
        """, (new_barangay, new_latitude, new_longitude, mic_id))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()