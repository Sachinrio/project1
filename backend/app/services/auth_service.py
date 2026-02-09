from datetime import datetime, timedelta
import secrets
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from google.oauth2 import id_token
from google.auth.transport import requests

from app.models.schemas import User, UserCreate, Token, GoogleToken
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.email_utils import send_reset_email

GOOGLE_CLIENT_ID = "616951204268-dsfdjvqp7mfn41gingbs7oqntp8f4f5g.apps.googleusercontent.com"

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_user(self, user_create: UserCreate) -> User:
        # Check if user exists
        statement = select(User).where(User.email == user_create.email)
        result = await self.session.execute(statement)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create User
        hashed_pwd = get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_pwd,
            is_active=True
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def login_user(self, email: str, password: str) -> Token:
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        user = result.scalars().first()

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return self._create_token(user.email)

    async def google_login(self, token_data: GoogleToken) -> Token:
        try:
            idinfo = id_token.verify_oauth2_token(
                token_data.token, 
                requests.Request(), 
                GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=5
            )
            email = idinfo.get("email")
            if not email:
                raise HTTPException(status_code=400, detail="Invalid Google Token: No email found")

            # Check or Create User
            statement = select(User).where(User.email == email)
            result = await self.session.execute(statement)
            user = result.scalars().first()

            if not user:
                random_password = secrets.token_urlsafe(16)
                hashed_pwd = get_password_hash(random_password)
                user = User(
                    email=email,
                    full_name=idinfo.get("name"),
                    hashed_password=hashed_pwd,
                    is_active=True
                )
                self.session.add(user)
                await self.session.commit()
            
            return self._create_token(user.email)

        except ValueError as e:
            raise HTTPException(status_code=401, detail=f"Invalid Google Token: {str(e)}")

    async def forgot_password_request(self, email: str):
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        user = result.scalars().first()

        if not user:
            # Security: Don't leak existence
            return {"message": "If this email is registered, you will receive a reset OTP."}

        # Generate OTP
        otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        user.reset_otp = otp
        user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        self.session.add(user)
        await self.session.commit()

        # Send Email (Robustness handled in utils)
        await send_reset_email(user.email, otp)
        
        return {"message": "OTP sent to your email."}

    async def reset_password(self, email: str, otp: str, new_password: str):
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        user = result.scalars().first()

        if not user:
             raise HTTPException(status_code=400, detail="Invalid request")

        if not user.reset_otp or user.reset_otp != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        if not user.otp_expires_at or user.otp_expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="OTP has expired")

        user.hashed_password = get_password_hash(new_password)
        user.reset_otp = None
        user.otp_expires_at = None
        
        self.session.add(user)
        await self.session.commit()
        
        return {"message": "Password reset successfully. You can now login."}

    def _create_token(self, email: str) -> Token:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
