import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class UserRole(str, enum.Enum):
    OWNER = "owner"
    STAFF = "staff"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.OWNER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    restaurants = relationship("Restaurant", back_populates="owner")


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(String(500))
    phone = Column(String(50))
    email = Column(String(255))
    logo_url = Column(String(500))
    qr_code_url = Column(String(500))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="restaurants")
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    restaurant = relationship("Restaurant", back_populates="categories")
    menu_items = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String(500))
    model_3d_url = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    preparation_time = Column(Integer, default=15)  # minutes
    calories = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    restaurant = relationship("Restaurant", back_populates="menu_items")
    category = relationship("Category", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(20), unique=True, nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    table_number = Column(String(50))
    customer_name = Column(String(255))
    customer_phone = Column(String(50))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_price = Column(Float, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    restaurant = relationship("Restaurant", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)
    notes = Column(Text)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")
