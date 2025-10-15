from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from app.routers.responder_backend.config import get_db_conn
from app.routers.responder_backend.utils import insert_log
import os
import time
from fastapi import Body

router = APIRouter()

GALLERY_DIR = os.path.join(os.path.dirname(__file__), "gallery_photos")

@router.post("/profile/upload_gallery_photo")
async def upload_gallery_photo(responder_id: int = Form(...), file: UploadFile = File(...)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM responder_gallery WHERE responder_id = %s",
            (responder_id,)
        )
        count = cursor.fetchone()[0]
        if count >= 10:
            raise HTTPException(status_code=400, detail="Maximum 10 photos allowed.")
        os.makedirs(GALLERY_DIR, exist_ok=True)
        ext = os.path.splitext(file.filename)[1]
        filename = f"{responder_id}_{int(time.time())}{ext}"
        file_path = os.path.join(GALLERY_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        cursor.execute(
            "INSERT INTO responder_gallery (responder_id, filename) VALUES (%s, %s)",
            (responder_id, filename)
        )
        conn.commit()
        # Log gallery upload (after commit)
        insert_log(
            responder_id,
            "gallery_upload",
            f"Uploaded gallery photo '{filename}'"
        )
        return {"success": True, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

class DeletePhotoRequest(BaseModel):
    responder_id: int
    filename: str

@router.post("/profile/delete_gallery_photo")
def delete_gallery_photo(data: DeletePhotoRequest):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM responder_gallery WHERE responder_id = %s AND filename = %s",
            (data.responder_id, data.filename)
        )
        conn.commit()
        file_path = os.path.join(GALLERY_DIR, data.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        # Log gallery delete (after commit)
        insert_log(
            data.responder_id,
            "gallery_delete",
            f"Deleted gallery photo '{data.filename}'"
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()
@router.post("/update_responder_profile")
def update_responder_profile(
    responder_id: int = Body(...),
    full_name: str = Body(...),
    phone: str = Body(...),
    email: str = Body(...),
    address: str = Body(...)
):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE responders
            SET full_name = %s, phone = %s, email = %s, address = %s
            WHERE id = %s
            """,
            (full_name, phone, email, address, responder_id)
        )
        conn.commit()
        # Log profile update
        insert_log(
            responder_id,
            "profile_update",
            f"Updated profile: name='{full_name}', phone='{phone}', email='{email}', address='{address}'"
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()