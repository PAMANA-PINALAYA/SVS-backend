from fastapi import APIRouter
from app.routers.responder_backend.config import get_db_conn

router = APIRouter()

@router.get("/get_tipsresources")
def get_tipsresources():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description, resource_type, link, created_by, created_at, updated_at
        FROM tips_resources
        ORDER BY id DESC
    """)
    resources = cursor.fetchall()
    resource_list = [
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "resource_type": row[3],
            "link": row[4],
            "created_by": row[5],
            "created_at": str(row[6]),
            "updated_at": str(row[7])
        }
        for row in resources
    ]
    cursor.close()
    conn.close()
    return {"resources": resource_list}