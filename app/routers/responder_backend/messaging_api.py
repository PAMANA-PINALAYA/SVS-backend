from fastapi import FastAPI
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, Query, Body

import os
from app.routers.responder_backend.config import get_db_conn, MESSAGE_IMG_DIR

router = APIRouter()

class SendMessageRequest(BaseModel):
    conversation_id: int
    sender_id: int
    sender_role: str
    content: str

class CreateConversationRequest(BaseModel):
    participant_ids: list[int]
    participant_roles: list[str]
    is_group: bool = False


@router.get("/messaging/contacts")
def get_contacts(user_id: int, user_role: str):
    conn = get_db_conn()
    cursor = conn.cursor()
    contacts = []
    try:
        # Responders
        cursor.execute("SELECT id, full_name, 'Responder' as role, photo FROM responders WHERE id != %s", (user_id,))
        contacts += [{"id": r[0], "name": r[1], "role": r[2], "photo": r[3]} for r in cursor.fetchall()]

        # Admins
        cursor.execute("SELECT id, full_name, 'Admin' as role, photo FROM admin_users")
        contacts += [{"id": r[0], "name": r[1], "role": r[2], "photo": r[3]} for r in cursor.fetchall()]

        # Superadmins
        cursor.execute("SELECT id, full_name, 'Superadmin' as role, photo FROM superadmin_users")
        contacts += [{"id": r[0], "name": r[1], "role": r[2], "photo": r[3]} for r in cursor.fetchall()]

        return {"contacts": contacts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/messaging/create_conversation")
def create_conversation(data: CreateConversationRequest):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO conversations (is_group) VALUES (%s) RETURNING id",
            (data.is_group,)
        )
        conv_id = cursor.fetchone()[0]
        for uid, role in zip(data.participant_ids, data.participant_roles):
            cursor.execute(
                "INSERT INTO conversation_participants (conversation_id, user_id, user_role) VALUES (%s, %s, %s)",
                (conv_id, uid, role)
            )
        conn.commit()
        return {"conversation_id": conv_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/messaging/conversations")
def get_conversations(user_id: int = Query(...)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.id, c.is_group, c.created_at,
                   (
                     SELECT sent_at FROM messages m
                     WHERE m.conversation_id = c.id
                     ORDER BY sent_at DESC
                     LIMIT 1
                   ) as last_message_time,
                   ARRAY(
                     SELECT user_id FROM conversation_participants cp2 WHERE cp2.conversation_id = c.id
                   ) as participant_ids,
                   (
                     SELECT content FROM messages m
                     WHERE m.conversation_id = c.id
                     ORDER BY sent_at DESC
                     LIMIT 1
                   ) as last_message,
                   (
                     SELECT sender_id FROM messages m
                     WHERE m.conversation_id = c.id
                     ORDER BY sent_at DESC
                     LIMIT 1
                   ) as last_message_sender_id,
                   (
                     SELECT is_read FROM messages m
                     WHERE m.conversation_id = c.id
                     ORDER BY sent_at DESC
                     LIMIT 1
                   ) as last_message_is_read
            FROM conversations c
            JOIN conversation_participants cp ON cp.conversation_id = c.id
            WHERE cp.user_id = %s
            ORDER BY last_message_time DESC NULLS LAST, c.created_at DESC
        """, (user_id,))
        conversations = []
        for r in cursor.fetchall():
            # unread_count: messages not read and not sent by current user
            cursor.execute("""
                SELECT COUNT(*) FROM messages
                WHERE conversation_id = %s AND is_read = FALSE AND sender_id != %s
            """, (r[0], user_id))
            unread_count = cursor.fetchone()[0]

            # Determine last message status
            last_message = r[5] or ""
            last_message_sender_id = r[6]
            last_message_is_read = r[7]
            last_status = ""
            if last_message_sender_id == user_id:
                last_status = "Seen" if last_message_is_read else "Sent"
            else:
                last_status = "Unread" if not last_message_is_read else "Seen"

            conversations.append({
                "id": r[0],
                "is_group": r[1],
                "created_at": r[2],
                "last_message_time": r[3],
                "participant_ids": r[4],
                "last_message": last_message,
                "last_message_sender_id": last_message_sender_id,
                "last_message_is_read": last_message_is_read,
                "last_message_status": last_status,
                "unread_count": unread_count
            })
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/messaging/messages")
def get_messages(conversation_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT sender_id, sender_role, content, sent_at, image_filename
            FROM messages
            WHERE conversation_id = %s
            ORDER BY sent_at ASC
        """, (conversation_id,))
        messages = []
        for r in cursor.fetchall():
            image_url = None
            if r[4]:
                image_url = f"http://127.0.0.1:8000/message_images/{r[4]}"
            messages.append({
                "sender_id": r[0],
                "sender_role": r[1],
                "content": r[2],
                "sent_at": r[3],
                "image_url": image_url
            })
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/messaging/send_message")
def send_message(data: SendMessageRequest):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO messages (conversation_id, sender_id, sender_role, content) VALUES (%s, %s, %s, %s)",
            (data.conversation_id, data.sender_id, data.sender_role, data.content)
        )
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/messaging/send_message_with_image")
async def send_message_with_image(
    conversation_id: int = Form(...),
    sender_id: int = Form(...),
    sender_role: str = Form(...),
    content: str = Form(""),
    image: UploadFile = File(None)
):
    conn = get_db_conn()
    cursor = conn.cursor()
    image_filename = None
    try:
        if image:
            os.makedirs(MESSAGE_IMG_DIR, exist_ok=True)
            image_filename = f"{conversation_id}_{sender_id}_{image.filename}"
            image_path = os.path.join(MESSAGE_IMG_DIR, image_filename)
            with open(image_path, "wb") as f:
                f.write(await image.read())
        cursor.execute(
            """
            INSERT INTO messages (conversation_id, sender_id, sender_role, content, image_filename)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (conversation_id, sender_id, sender_role, content, image_filename)
        )
        conn.commit()
        return JSONResponse({"success": True, "message_id": cursor.fetchone()[0]})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/messaging/messages")
def get_messages(conversation_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, sender_id, sender_role, content, sent_at, image_filename, is_read
            FROM messages
            WHERE conversation_id = %s
            ORDER BY sent_at ASC
        """, (conversation_id,))
        messages = []
        for r in cursor.fetchall():
            image_url = None
            if r[5]:
                image_url = f"http://127.0.0.1:8000/message_images/{r[5]}"
            messages.append({
                "id": r[0],
                "sender_id": r[1],
                "sender_role": r[2],
                "content": r[3],
                "sent_at": r[4],
                "image_url": image_url,
                "is_read": r[6],
            })
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/messaging/mark_as_read")
def mark_as_read(conversation_id: int = Body(...), user_id: int = Body(...)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE messages
            SET is_read = TRUE
            WHERE conversation_id = %s AND sender_id != %s AND is_read = FALSE
        """, (conversation_id, user_id))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/messaging/conversations")
def get_conversations(user_id: int = Query(...)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.id, c.is_group, c.created_at,
                   (SELECT MAX(sent_at) FROM messages m WHERE m.conversation_id = c.id) as last_message_time,
                   ARRAY(
                     SELECT user_id FROM conversation_participants cp2 WHERE cp2.conversation_id = c.id
                   ) as participant_ids,
                   (
                     SELECT is_read FROM messages m
                     WHERE m.conversation_id = c.id
                     ORDER BY sent_at DESC
                     LIMIT 1
                   ) as last_is_read,
                   (
                     SELECT sender_id FROM messages m
                     WHERE m.conversation_id = c.id
                     ORDER BY sent_at DESC
                     LIMIT 1
                   ) as last_sender_id
            FROM conversations c
            JOIN conversation_participants cp ON cp.conversation_id = c.id
            WHERE cp.user_id = %s
            ORDER BY last_message_time DESC NULLS LAST, c.created_at DESC
        """, (user_id,))
        conversations = []
        for r in cursor.fetchall():
            # unread_count: messages not read and not sent by current user
            cursor.execute("""
                SELECT COUNT(*) FROM messages
                WHERE conversation_id = %s AND is_read = FALSE AND sender_id != %s
            """, (r[0], user_id))
            unread_count = cursor.fetchone()[0]
            # Determine last message status
            last_status = "Sent"
            if r[6] == user_id:
                last_status = "Seen" if r[5] else "Sent"
            elif r[5] is False and r[6] != user_id:
                last_status = "Unread"
            elif r[5] is True and r[6] != user_id:
                last_status = "Seen"
            conversations.append({
                "id": r[0],
                "is_group": r[1],
                "created_at": r[2],
                "last_message_time": r[3],
                "participant_ids": r[4],
                "unread_count": unread_count,
                "last_message_status": last_status
            })
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()