import random
import string
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import MenuItem, Order, OrderItem, OrderStatus, Restaurant, User
from ..schemas import OrderCreate, OrderResponse, OrderStatusUpdate
from ..utils.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


def _generate_order_number(db: Session) -> str:
    while True:
        number = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not db.query(Order).filter(Order.order_number == number).first():
            return number


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.id == data.restaurant_id, Restaurant.is_active == True)
        .first()
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    total_price = 0.0
    resolved_items = []

    for item_data in data.items:
        menu_item = (
            db.query(MenuItem)
            .filter(
                MenuItem.id == item_data.menu_item_id,
                MenuItem.restaurant_id == data.restaurant_id,
                MenuItem.is_available == True,
            )
            .first()
        )
        if not menu_item:
            raise HTTPException(
                status_code=400,
                detail=f"Menu item {item_data.menu_item_id} not found or unavailable",
            )
        total_price += menu_item.price * item_data.quantity
        resolved_items.append(
            {
                "menu_item_id": menu_item.id,
                "price": menu_item.price,
                "quantity": item_data.quantity,
                "notes": item_data.notes,
            }
        )

    order = Order(
        order_number=_generate_order_number(db),
        restaurant_id=data.restaurant_id,
        table_number=data.table_number,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        notes=data.notes,
        total_price=total_price,
    )
    db.add(order)
    db.flush()

    for it in resolved_items:
        db.add(OrderItem(order_id=order.id, **it))

    db.commit()
    db.refresh(order)
    return order


@router.get("/restaurant/{restaurant_id}", response_model=List[OrderResponse])
def get_restaurant_orders(
    restaurant_id: int,
    order_status: Optional[OrderStatus] = None,
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

    query = db.query(Order).filter(Order.restaurant_id == restaurant_id)
    if order_status:
        query = query.filter(Order.status == order_status)
    return query.order_by(Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .join(Restaurant)
        .filter(Order.id == order_id, Restaurant.owner_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .join(Restaurant)
        .filter(Order.id == order_id, Restaurant.owner_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = data.status
    db.commit()
    db.refresh(order)
    return order
