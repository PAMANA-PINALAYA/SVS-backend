from fastapi import APIRouter

router = APIRouter()

@router.post("/admin/logout")
def admin_logout():
    # Implement session/token invalidation here if needed
    return {"success": True, "message": "Logged out."}