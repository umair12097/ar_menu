import os
import uuid

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import MenuItem, Restaurant, User
from ..utils.auth import get_current_user

router = APIRouter(prefix="/upload", tags=["File Upload"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_MODEL_SIZE = 50 * 1024 * 1024   # 50 MB


async def _save_file(file: UploadFile, directory: str) -> str:
    os.makedirs(directory, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1].lower()
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(directory, filename)
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(await file.read())
    return filename


@router.post("/image/menu-item/{item_id}")
async def upload_menu_item_image(
    item_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type. Allowed: JPEG, PNG, WebP, GIF")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large. Max size is 10 MB")
    await file.seek(0)

    item = (
        db.query(MenuItem)
        .join(Restaurant)
        .filter(MenuItem.id == item_id, Restaurant.owner_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    upload_dir = os.path.join(settings.UPLOAD_DIR, "images")
    filename = await _save_file(file, upload_dir)
    item.image_url = f"/uploads/images/{filename}"
    db.commit()
    return {"url": item.image_url}


@router.post("/model/menu-item/{item_id}")
async def upload_menu_item_model(
    item_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".glb", ".gltf"}:
        raise HTTPException(status_code=400, detail="Invalid model type. Allowed: .glb, .gltf")

    content = await file.read()
    if len(content) > MAX_MODEL_SIZE:
        raise HTTPException(status_code=400, detail="Model too large. Max size is 50 MB")
    await file.seek(0)

    item = (
        db.query(MenuItem)
        .join(Restaurant)
        .filter(MenuItem.id == item_id, Restaurant.owner_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    upload_dir = os.path.join(settings.UPLOAD_DIR, "models")
    filename = await _save_file(file, upload_dir)
    item.model_3d_url = f"/uploads/models/{filename}"
    db.commit()
    return {"url": item.model_3d_url}


@router.post("/logo/restaurant/{restaurant_id}")
async def upload_restaurant_logo(
    restaurant_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type. Allowed: JPEG, PNG, WebP")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large. Max size is 10 MB")
    await file.seek(0)

    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == restaurant_id, Restaurant.owner_id == current_user.id)
        .first()
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    upload_dir = os.path.join(settings.UPLOAD_DIR, "logos")
    filename = await _save_file(file, upload_dir)
    restaurant.logo_url = f"/uploads/logos/{filename}"
    db.commit()
    return {"url": restaurant.logo_url}
