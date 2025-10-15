from fastapi import APIRouter, HTTPException
from app.routers.responder_backend.config import get_db_conn
import json

router = APIRouter()

@router.get("/get_history_reports")
def get_history_reports(responder_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, report_title, description, category, status, photos, submitted_at
            FROM responders_report
            WHERE responder_id = %s AND status NOT IN ('Not Resolved', 'Pending')
            ORDER BY id DESC
            """,
            (responder_id,)
        )
        history = []
        for row in cursor.fetchall():
            photos = []
            if row[5]:
                try:
                    photos = json.loads(row[5])
                except Exception:
                    photos = []
            history.append({
                "id": row[0],
                "report_title": row[1],
                "description": row[2],
                "category": row[3],
                "status": row[4],
                "photos": photos,
                "submitted_at": row[6].strftime("%Y-%m-%d %H:%M"),
            })
        return {"history": history}
    except Exception as e:
        print("Get history reports error:", e)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()