# from typing import List

# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from ..database import get_db
# from ..models import Restaurant, User
# from ..schemas import (
#     RestaurantCreate,
#     RestaurantMenuResponse,
#     RestaurantResponse,
#     RestaurantUpdate,
# )
# from ..utils.auth import get_current_user
# from ..utils.qr_generator import generate_qr_code

# router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


# @router.post("/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
# def create_restaurant(
#     data: RestaurantCreate,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     restaurant = Restaurant(**data.model_dump(), owner_id=current_user.id)
#     db.add(restaurant)
#     db.commit()
#     db.refresh(restaurant)

#     qr_url = generate_qr_code(restaurant.id)
#     restaurant.qr_code_url = qr_url
#     db.commit()
#     db.refresh(restaurant)

#     return restaurant


# @router.get("/my", response_model=List[RestaurantResponse])
# def get_my_restaurants(
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     return db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).all()


# @router.get("/{restaurant_id}", response_model=RestaurantMenuResponse)
# def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
#     restaurant = (
#         db.query(Restaurant)
#         .filter(Restaurant.id == restaurant_id, Restaurant.is_active == True)
#         .first()
#     )
#     if not restaurant:
#         raise HTTPException(status_code=404, detail="Restaurant not found")
#     return restaurant


# @router.put("/{restaurant_id}", response_model=RestaurantResponse)
# def update_restaurant(
#     restaurant_id: int,
#     data: RestaurantUpdate,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     restaurant = (
#         db.query(Restaurant)
#         .filter(Restaurant.id == restaurant_id, Restaurant.owner_id == current_user.id)
#         .first()
#     )
#     if not restaurant:
#         raise HTTPException(status_code=404, detail="Restaurant not found")

#     for key, value in data.model_dump(exclude_unset=True).items():
#         setattr(restaurant, key, value)

#     db.commit()
#     db.refresh(restaurant)
#     return restaurant


# @router.post("/{restaurant_id}/regenerate-qr", response_model=RestaurantResponse)
# def regenerate_qr(
#     restaurant_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     restaurant = (
#         db.query(Restaurant)
#         .filter(Restaurant.id == restaurant_id, Restaurant.owner_id == current_user.id)
#         .first()
#     )
#     if not restaurant:
#         raise HTTPException(status_code=404, detail="Restaurant not found")

#     restaurant.qr_code_url = generate_qr_code(restaurant.id)
#     db.commit()
#     db.refresh(restaurant)
#     return restaurant
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantRead
from app.utils.qr_generator import generate_qr_code
from app.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=RestaurantRead)
def create_restaurant(
    restaurant_in: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Step 1: Create restaurant first to get the ID
    restaurant = Restaurant(
        name=restaurant_in.name,
        description=restaurant_in.description,
        address=restaurant_in.address,
        phone=restaurant_in.phone,
        email=restaurant_in.email,
        owner_id=current_user.id,
        is_active=True,
        # logo_url and qr_code_url will be added later if needed
    )

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)   # This is important to get the generated ID

    # Step 2: Generate QR Code and save it
    try:
        qr_code_value = generate_qr_code(restaurant.id)
        
        # Update the restaurant with QR code
        restaurant.qr_code_url = qr_code_value
        db.commit()
        db.refresh(restaurant)
        
        print(f"QR Code generated successfully for restaurant ID: {restaurant.id}")
        
    except Exception as e:
        print(f"Warning: Failed to generate QR code for restaurant {restaurant.id}: {e}")
        # We still return the restaurant even if QR code fails
        # You can also raise an error here if QR code is mandatory

    return restaurant
