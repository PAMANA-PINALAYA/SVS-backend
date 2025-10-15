import os
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles

# Get DATABASE_URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # fallback for local testing
    DB_USER = "postgres"
    DB_PASS = "123"
    DB_HOST = "localhost"
    DB_NAME = "SmartSurveillanceSystem"
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# SQLAlchemy engine & session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(
    title="Smart Surveillance System API",
    description="Backend API for Smart Surveillance System",
    version="1.0.0"
)

# Include responder backend router
from app.routers.responder_backend.responder_main import router as responder_router
app.include_router(responder_router)

# Include SAAdmin backend main router
from app.routers.SAAdmin_backend.SAAdmin_main import router as saadmin_router
app.include_router(saadmin_router)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mount static directories (adjust paths as needed)
ROUTER_DIR = os.path.join(os.path.dirname(__file__), "app", "routers", "responder_backend")
app.mount("/patrol_photos", StaticFiles(directory=os.path.join(ROUTER_DIR, "patrol_photos")), name="patrol_photos")
app.mount("/profile_pictures", StaticFiles(directory=os.path.join(ROUTER_DIR, "uploaded_profile_picture")), name="profile_pictures")
app.mount("/gallery_photos", StaticFiles(directory=os.path.join(ROUTER_DIR, "gallery_photos")), name="gallery_photos")
app.mount("/uploaded_photos", StaticFiles(directory=os.path.join(ROUTER_DIR, "uploaded_photos")), name="uploaded_photos")
app.mount("/message_images", StaticFiles(directory=os.path.join(ROUTER_DIR, "message_images")), name="message_images")
app.mount("/uploaded_profile_picture", StaticFiles(directory=os.path.join(ROUTER_DIR, "uploaded_profile_picture")), name="uploaded_profile_picture")

# Run with correct port on Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # Render sets PORT
    uvicorn.run(app, host="0.0.0.0", port=port)
