from fastapi import APIRouter, HTTPException
import psycopg2
import os

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

@router.get("/admin/cameras")
def get_cameras():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, type, url, city, barangay, street, exact_location,
                   ai_supported, mic_supported, night_vision, status, resolution, frame_rate,
                   poe_powered, dc_powered, storage_supported, field_of_view, brand, model,
                   latitude, longitude
            FROM cctv_cameras
            ORDER BY id DESC
        """)
        return [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/microphones")
def get_microphones():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, type, city, barangay, street, exact_location,
                   ai_supported, noise_reduction, sensitivity_db, poe_powered, dc_powered,
                   esp32_version, mic_model, status
            FROM microphones
            ORDER BY id DESC
        """)
        return [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/device/status")
def update_device_status(device_type: str, device_id: int, status: str):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        table = "cctv_cameras" if device_type == "cctv" else "microphones"
        cursor.execute(f"UPDATE {table} SET status = %s WHERE id = %s", (status, device_id))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/device/delete")
def delete_device(device_type: str, device_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        table = "cctv_cameras" if device_type == "cctv" else "microphones"
        cursor.execute(f"DELETE FROM {table} WHERE id = %s", (device_id,))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/device/edit")
def edit_device(device_type: str, device_id: int, data: dict):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        table = "cctv_cameras" if device_type == "cctv" else "microphones"
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        values = list(data.values()) + [device_id]
        cursor.execute(f"UPDATE {table} SET {set_clause} WHERE id = %s", values)
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/device/integrate")
def integrate_devices(cctv_id: int, mic_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO device_integration (cctv_id, microphone_id, link_type, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (cctv_id, mic_id, 'audio-video'))
        cursor.execute("UPDATE cctv_cameras SET integrated_mic_id = %s WHERE id = %s", (mic_id, cctv_id))
        cursor.execute("UPDATE microphones SET integrated_cctv_id = %s WHERE id = %s", (cctv_id, mic_id))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/device/integrations")
def get_integrations():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.name, m.name, di.link_type, di.created_at
            FROM device_integration di
            JOIN cctv_cameras c ON di.cctv_id = c.id
            JOIN microphones m ON di.microphone_id = m.id
            ORDER BY di.created_at DESC
        """)
        return [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/device/disintegrate")
def disintegrate_device(cctv_name: str, mic_name: str):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM cctv_cameras WHERE name = %s", (cctv_name,))
        cctv_row = cursor.fetchone()
        cursor.execute("SELECT id FROM microphones WHERE name = %s", (mic_name,))
        mic_row = cursor.fetchone()
        if not cctv_row or not mic_row:
            return {"success": False}
        cctv_id, mic_id = cctv_row[0], mic_row[0]
        cursor.execute("""
            DELETE FROM device_integration
            WHERE cctv_id = %s AND microphone_id = %s
        """, (cctv_id, mic_id))
        cursor.execute("UPDATE cctv_cameras SET integrated_mic_id = NULL WHERE id = %s", (cctv_id,))
        cursor.execute("UPDATE microphones SET integrated_cctv_id = NULL WHERE id = %s", (mic_id,))
        conn.commit()
        return {"success": True}
    finally:
        cursor.close()
        conn.close()