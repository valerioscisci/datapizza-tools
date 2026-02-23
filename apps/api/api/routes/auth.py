from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import User
from api.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from api.auth import hash_password, verify_password, create_access_token, get_current_user
from api.utils import safe_parse_json_list

router = APIRouter(prefix="/auth", tags=["Auth"])


def _user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        bio=user.bio,
        location=user.location,
        experience_level=user.experience_level,
        experience_years=user.experience_years,
        current_role=user.current_role,
        skills=safe_parse_json_list(user.skills_json),
        availability_status=user.availability_status or "available",
        reskilling_status=user.reskilling_status,
        adopted_by_company=user.adopted_by_company,
        created_at=user.created_at,
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.is_active == 1).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return _user_to_response(current_user)
