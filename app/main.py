# import os

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles

# from .config import settings
# from .database import Base, engine
# from .routers import auth, menu, orders, restaurants, upload

# # Create tables on startup
# Base.metadata.create_all(bind=engine)

# # Ensure upload directories exist
# for sub in ("images", "models", "logos", "qrcodes"):
#     os.makedirs(os.path.join(settings.UPLOAD_DIR, sub), exist_ok=True)

# app = FastAPI(
#     title="AR Menu API",
#     description="Augmented Reality Restaurant Menu Platform",
#     version="1.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc",
# )

# # CORS — allow the Next.js dev server
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:3001", "https://ar-menu-nextjs.vercel.app", "https://ar-menu-nextjs-*.vercel.app"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Serve uploaded files
# app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# # Register routers
# app.include_router(auth.router)
# app.include_router(restaurants.router)
# app.include_router(menu.router)
# app.include_router(orders.router)
# app.include_router(upload.router)


# @app.get("/", tags=["Health"])
# def root():
#     return {"message": "AR Menu API is running", "docs": "/docs"}


# @app.get("/health", tags=["Health"])
# def health_check():
#     return {"status": "healthy"}

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import Base, engine
from .routers import auth, menu, orders, restaurants, upload

# Create tables
Base.metadata.create_all(bind=engine)

# Create upload directories
for sub in ("images", "models", "logos", "qrcodes"):
    os.makedirs(os.path.join(settings.UPLOAD_DIR, sub), exist_ok=True)

app = FastAPI(
    title="AR Menu API",
    description="Augmented Reality Restaurant Menu Platform",
    version="1.0.0",
)

# ====================== CORS MUST BE ADDED EARLY ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ar-menu-nextjs.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_origin_regex=r"https://ar-menu-nextjs-.*\.vercel\.app",  # ✅ replaces wildcard string
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers AFTER CORS
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(restaurants.router, prefix="/restaurants", tags=["restaurants"])
app.include_router(menu.router, prefix="/menu", tags=["menu"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])

@app.get("/", tags=["Health"])
def root():
    return {"message": "AR Menu API is running", "docs": "/docs"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
