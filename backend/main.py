from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from db.session import engine
from auth.router import router as auth_router
from complaint.router import router as complaint_router
from priority_engine.router import router as priority_router
from admin.router import router as admin_router
from notification.router import router as notification_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    import models  # Ensure models are loaded before create_all
    models.Base.metadata.create_all(bind=engine)
    print("Database tables created")
    
    # Initialize location trie with existing locations
    from db.session import SessionLocal
    from models import Location
    from priority_engine.engine import get_location_trie
    
    db = SessionLocal()
    try:
        locations = db.query(Location).all()
        trie = get_location_trie()
        trie.build_from_locations(locations)
        print(f"Location trie built with {len(locations)} locations")
    finally:
        db.close()
    
    yield
    
    # Shutdown
    print("Shutting down")


app = FastAPI(
    title="Civic Complaint Prioritization System",
    description="API for civic complaint reporting, prioritization, and management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(complaint_router)
app.include_router(priority_router)
app.include_router(admin_router)
app.include_router(notification_router)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "civic-complaint-api"}


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Civic Complaint Prioritization System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Static files for uploaded evidence
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)