from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
import schemas
from database import get_db, engine, Base
from config import settings

# Import routers
from routes_objects import router as objects_router
from routes_defects import router as defects_router
from routes_dashboard import router as dashboard_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="OKS Expert System",
    description="System for construction and facility management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "OKS Expert System API",
        "version": "1.0.0",
        "description": "System for construction and facility management in Moscow region",
        "docs": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Include routers
app.include_router(objects_router)
app.include_router(defects_router)
app.include_router(dashboard_router)


# Auth endpoint (simplified for demo)
@app.post("/api/auth/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    """Login endpoint - simplified for demo purposes"""
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # In production, verify password hash here
    # For demo, accept any password for existing users
    
    return {
        "access_token": f"demo-token-{user.id}",
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }


# Users endpoint
@app.get("/api/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    return db.query(models.User).filter(models.User.is_active == True).all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
