from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from db.session import get_db
from models import User, Citizen, Admin, UserRole
from schemas import UserCreate, UserLogin, UserResponse, Token, CitizenProfile, AdminProfile
from common.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    require_admin
)
from common.exceptions import ValidationException, ConflictException, UnauthorizedException

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    citizen_profile: CitizenProfile = None,
    admin_profile: AdminProfile = None,
    db: Session = Depends(get_db)
):
    """Register a new user (citizen or admin)"""
    # Check if user exists
    existing = db.query(User).filter(
        (User.email == user_data.email) | (User.phone == user_data.phone)
    ).first()
    if existing:
        raise ConflictException("User with this email or phone already exists")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role
    )
    db.add(user)
    db.flush()
    
    # Create role-specific profile
    if user_data.role == UserRole.CITIZEN:
        profile = Citizen(
            user_id=user.id,
            address=citizen_profile.address if citizen_profile else None,
            preferred_notification_channels=citizen_profile.preferred_notification_channels if citizen_profile else "email,push"
        )
        db.add(profile)
    elif user_data.role == UserRole.ADMIN:
        profile = Admin(
            user_id=user.id,
            department_id=admin_profile.department_id if admin_profile else None,
            permissions=admin_profile.permissions if admin_profile else "all"
        )
        db.add(profile)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictException("Registration failed")
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """User login"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")
    
    if not user.is_active:
        raise UnauthorizedException("Account is deactivated")
    
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    from common.auth import decode_token
    
    token_data = decode_token(refresh_token)
    if not token_data or token_data.user_id is None:
        raise UnauthorizedException("Invalid refresh token")
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")
    
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    full_name: str = None,
    phone: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    if full_name:
        current_user.full_name = full_name
    if phone:
        # Check if phone is already taken
        existing = db.query(User).filter(User.phone == phone, User.id != current_user.id).first()
        if existing:
            raise ConflictException("Phone number already in use")
        current_user.phone = phone
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/logout")
async def logout():
    """Logout (client-side token removal)"""
    return {"message": "Logged out successfully"}