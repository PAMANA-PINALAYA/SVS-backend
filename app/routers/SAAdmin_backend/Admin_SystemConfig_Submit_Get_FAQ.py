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

@router.get("/admin/faqs")
def get_faqs():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, question, answer FROM faqs ORDER BY id DESC")
        faqs = cursor.fetchall()
        return [{"id": row[0], "question": row[1], "answer": row[2]} for row in faqs]
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/faqs/add")
def post_faq(question: str, answer: str):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO faqs (question, answer) VALUES (%s, %s)", (question, answer))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/faqs/edit")
def edit_faq(faq_id: int, question: str, answer: str):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE faqs SET question=%s, answer=%s WHERE id=%s", (question, answer, faq_id))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/faqs/delete")
def delete_faq(faq_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM faqs WHERE id=%s", (faq_id,))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()