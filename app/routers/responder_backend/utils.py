from app.routers.responder_backend.config import get_db_conn

def insert_log(user_id, action_type, description, related_id=None):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT photo, full_name FROM responders WHERE id = %s", (user_id,)
    )
    row = cursor.fetchone()
    profile_photo = row[0] if row and row[0] else "profile.png"
    user_name = row[1] if row and row[1] else "Unknown Responder"
    role = "Responder"
    user_type = "responder"
    cursor.execute(
        """
        INSERT INTO admin_responder_logs (
            user_id, user_type, role, action_type, description, related_id, user_name, user_photo
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (user_id, user_type, role, action_type, description, related_id, user_name, profile_photo)
    )
    conn.commit()
    cursor.close()
    conn.close()