from fastapi import APIRouter, HTTPException
from app.routers.responder_backend.config import get_db_conn

router = APIRouter()

@router.get("/get_responder_profile")
def get_responder_profile(responder_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT full_name, phone, email, address, photo
            FROM responders
            WHERE id = %s
            """,
            (responder_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Responder not found")
        return {
            "full_name": row[0],
            "phone": row[1],
            "email": row[2],
            "address": row[3],
            "photo": row[4],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()