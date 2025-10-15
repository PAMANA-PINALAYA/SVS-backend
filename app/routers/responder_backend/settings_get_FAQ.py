from fastapi import APIRouter
from app.routers.responder_backend.config import get_db_conn

router = APIRouter()

@router.get("/get_faqs")
def get_faqs():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, answer FROM faqs ORDER BY id DESC")
    faqs = cursor.fetchall()
    faq_list = [{"id": row[0], "question": row[1], "answer": row[2]} for row in faqs]
    cursor.close()
    conn.close()
    return {"faqs": faq_list}