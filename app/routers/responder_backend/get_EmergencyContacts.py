from fastapi import APIRouter
from app.routers.responder_backend.config import get_db_conn

router = APIRouter()

@router.get("/get_emergencycontacts")
def get_emergencycontacts():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, phone, role, address, is_active, created_by, created_at, updated_at
        FROM emergency_contacts
        WHERE is_active = TRUE
        ORDER BY name ASC
    """)
    contacts = cursor.fetchall()
    contact_list = [
        {
            "id": row[0],
            "name": row[1],
            "phone": row[2],
            "role": row[3],
            "address": row[4],
            "is_active": row[5],
            "created_by": row[6],
            "created_at": str(row[7]),
            "updated_at": str(row[8])
        }
        for row in contacts
    ]
    cursor.close()
    conn.close()
    return {"contacts": contact_list}