from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category, MenuItem, Restaurant, User
from ..schemas import (
    CategoryCreate,
    CategoryResponse,
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
    RatingCreate,
)
from ..utils.auth import get_current_user

router = APIRouter(tags=["Menu"])


# ── Categories ────────────────────────────────────────────────────────────────

@router.post(
    "/restaurants/{restaurant_id}/categories",
    response_model=CategoryResponse,
    status_code=201,
)
def create_category(
    restaurant_id: int,
    data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == restaurant_id, Restaurant.owner_id == current_user.id)
        .first()
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    category = Category(**data.model_dump(), restaurant_id=restaurant_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/restaurants/{restaurant_id}/categories", response_model=List[CategoryResponse])
def get_categories(restaurant_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Category)
        .filter(Category.restaurant_id == restaurant_id)
        .order_by(Category.sort_order)
        .all()
    )


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = (
        db.query(Category)
        .join(Restaurant)
        .filter(Category.id == category_id, Restaurant.owner_id == current_user.id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()


# ── Menu Items ────────────────────────────────────────────────────────────────

@router.post(
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItemResponse,
    status_code=201,
)
def create_menu_item(
    restaurant_id: int,
    data: MenuItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == restaurant_id, Restaurant.owner_id == current_user.id)
        .first()
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    item = MenuItem(**data.model_dump(), restaurant_id=restaurant_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/restaurants/{restaurant_id}/menu", response_model=List[MenuItemResponse])
def get_menu_items(
    restaurant_id: int,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id)
    if category_id:
        query = query.filter(MenuItem.category_id == category_id)
    return query.order_by(MenuItem.is_featured.desc(), MenuItem.created_at.desc()).all()


@router.get("/menu/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


@router.put("/menu/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    data: MenuItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(MenuItem)
        .join(Restaurant)
        .filter(MenuItem.id == item_id, Restaurant.owner_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/menu/{item_id}", status_code=204)
def delete_menu_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(MenuItem)
        .join(Restaurant)
        .filter(MenuItem.id == item_id, Restaurant.owner_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()


@router.post("/menu/{item_id}/rate", response_model=MenuItemResponse)
def rate_menu_item(
    item_id: int,
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # Rolling average
    total = item.rating * item.rating_count + rating_data.rating
    item.rating_count += 1
    item.rating = total / item.rating_count

    db.commit()
    db.refresh(item)
    return item
