from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from app.schemas import UserRegister, UserLogin, Token
from app.models import User
from app.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.deps import get_current_user, get_db
from app.dbconfig import settings



router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    existing_user = await db.execute(select(User).where(User.email == user.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_password)

    db.add(new_user)
    await db.commit()
    return {"message": "User created successfully"}


@router.post("/login", response_model=Token)
async def login(
    user: UserLogin, response: Response, db: AsyncSession = Depends(get_db)
):
    # Verify user credentials
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    # Generate tokens
    access_token = create_access_token(
        {"user_id": db_user.id, "token_version": db_user.token_version}
    )
    refresh_token = create_refresh_token(
        {"user_id": db_user.id, "token_version": db_user.token_version}
    )

    # Update user with new refresh token
    db_user.refresh_token = refresh_token
    db_user.refresh_token_expires = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    await db.commit()

    # Set secure cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=expires,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing"
        )

    try:
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("user_id")
        token_version = payload.get("token_version")

        # Verify user and token version
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if (
            not user
            or user.refresh_token != refresh_token
            or user.token_version != token_version
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Generate new tokens
        new_access_token = create_access_token(
            {"user_id": user.id, "token_version": user.token_version}
        )
       

       

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }

    except HTTPException:
        # Clear invalid tokens
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        raise


@router.get("/logout")
async def logout(
    response: Response,
   
   
):
   
    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {"id": user.id, "name": user.name, "email": user.email}
