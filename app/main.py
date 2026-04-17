import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, engine
from .routers import auth, menu, orders, restaurants, upload

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Ensure upload directories exist
for sub in ("images", "models", "logos", "qrcodes"):
    os.makedirs(os.path.join(settings.UPLOAD_DIR, sub), exist_ok=True)

app = FastAPI(
    title="AR Menu API",
    description="Augmented Reality Restaurant Menu Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow the Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:3001", "https://ar-menu-nextjs.vercel.app", "https://ar-menu-nextjs-*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Register routers
app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(upload.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "AR Menu API is running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
