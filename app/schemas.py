from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator

from .models import OrderStatus, UserRole


# ── User ────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ── Category ─────────────────────────────────────────────────────────────────

class CategoryBase(BaseModel):
    name: str
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    restaurant_id: int

    model_config = {"from_attributes": True}


# ── Menu Item ─────────────────────────────────────────────────────────────────

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None
    is_available: bool = True
    is_featured: bool = False
    preparation_time: int = 15
    calories: Optional[int] = None


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    is_available: Optional[bool] = None
    is_featured: Optional[bool] = None
    preparation_time: Optional[int] = None
    calories: Optional[int] = None


class MenuItemResponse(MenuItemBase):
    id: int
    restaurant_id: int
    image_url: Optional[str] = None
    model_3d_url: Optional[str] = None
    rating: float
    rating_count: int
    category: Optional[CategoryResponse] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Restaurant ───────────────────────────────────────────────────────────────

class RestaurantBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class RestaurantResponse(RestaurantBase):
    id: int
    owner_id: int
    logo_url: Optional[str] = None
    qr_code_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RestaurantMenuResponse(RestaurantResponse):
    menu_items: List[MenuItemResponse] = []
    categories: List[CategoryResponse] = []


# ── Order ─────────────────────────────────────────────────────────────────────

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1
    notes: Optional[str] = None


class OrderCreate(BaseModel):
    restaurant_id: int
    table_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    price: float
    notes: Optional[str] = None
    menu_item: Optional[MenuItemResponse] = None

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    order_number: str
    restaurant_id: int
    table_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    status: OrderStatus
    total_price: float
    notes: Optional[str] = None
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# ── Rating ───────────────────────────────────────────────────────────────────

class RatingCreate(BaseModel):
    rating: float

    @field_validator("rating")
    @classmethod
    def valid_rating(cls, v: float) -> float:
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v
