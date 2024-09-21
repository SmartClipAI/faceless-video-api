from sqlalchemy import Column, Integer, String, Boolean, DateTime, select
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.core.security import get_password_hash, verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from pydantic import BaseModel
from typing import Optional

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  
    is_active = Column(Boolean(), default=True)
    is_admin = Column(Boolean(), default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    async def create(cls, **kwargs):
        async with async_session() as session:
            user = cls(**kwargs)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    @classmethod
    async def get_by_username(cls, username: str) -> Optional['User']:
        async with async_session() as session:
            result = await session.execute(
                select(cls).where(cls.username == username)
            )
            return result.scalars().first()

    @classmethod
    async def get_by_email(cls, email: str) -> Optional['User']:
        async with async_session() as session:
            result = await session.execute(
                select(cls).where(cls.email == email)
            )
            return result.scalars().first()

    @classmethod
    async def authenticate(cls, username: str, password: str) -> Optional['User']:
        user = await cls.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def __repr__(self):
        return f"<User {self.username}>"