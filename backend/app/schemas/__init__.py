"""Schemas package initialization."""
from app.schemas.auth import Token, TokenPayload, UserLogin, UserRegister
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.space import SpaceBase, SpaceCreate, SpaceUpdate, SpaceResponse
from app.schemas.reservation import (
    ReservationBase,
    ReservationCreate,
    ReservationUpdate,
    ReservationResponse,
)

__all__ = [
    "Token",
    "TokenPayload",
    "UserLogin",
    "UserRegister",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "SpaceBase",
    "SpaceCreate",
    "SpaceUpdate",
    "SpaceResponse",
    "ReservationBase",
    "ReservationCreate",
    "ReservationUpdate",
    "ReservationResponse",
]
