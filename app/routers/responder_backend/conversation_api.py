from fastapi import APIRouter, Query, Form, UploadFile, File, HTTPException, Body
from app.routers.responder_backend.config import get_db_conn
import os
import time

router = APIRouter()

@router.get("/conversation/messages")
def get_messages(conversation_id: int = Query(...)):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, sender_id, content, sent_at, is_read, image_url
        FROM messages
        WHERE conversation_id = %s
        ORDER BY sent_at ASC
    """, (conversation_id,))
    messages = []
    for row in cursor.fetchall():
        messages.append({
            "id": row[0],
            "sender_id": row[1],
            "content": row[2],
            "sent_at": str(row[3]),
            "is_read": row[4],
            "image_url": row[5],
        })
    cursor.close()
    conn.close()
    return {"messages": messages}

@router.post("/conversation/send_message")
async def send_message(
    conversation_id: int = Form(...),
    sender_id: int = Form(...),
    content: str = Form(""),
    image: UploadFile = File(None)
):
    conn = get_db_conn()
    cursor = conn.cursor()
    image_url = None
    if image:
        ext = os.path.splitext(image.filename)[1]
        filename = f"{int(time.time())}_{sender_id}{ext}"
        file_path = os.path.join("uploaded_message_images", filename)
        with open(file_path, "wb") as f:
            f.write(await image.read())
        image_url = f"/uploaded_message_images/{filename}"
    cursor.execute("""
        INSERT INTO messages (conversation_id, sender_id, content, sent_at, is_read, image_url)
        VALUES (%s, %s, %s, NOW(), FALSE, %s)
    """, (conversation_id, sender_id, content, image_url))
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True}

@router.post("/conversation/mark_seen")
def mark_messages_as_seen(conversation_id: int = Body(...), user_id: int = Body(...)):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE messages
        SET is_read = TRUE
        WHERE conversation_id = %s AND sender_id != %s AND is_read = FALSE
    """, (conversation_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True}