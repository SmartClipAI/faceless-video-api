from app.db.base_class import Base
from sqlalchemy import Column, String, Float, DateTime, select
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError


class VideoTask(Base):
    __tablename__ = "video_tasks"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, index=True)
    progress = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    async def create(cls, **kwargs) -> Optional['VideoTask']:
        try:
            async with async_session() as session:
                task = cls(**kwargs)
                session.add(task)
                await session.commit()
                await session.refresh(task)
            return task
        except SQLAlchemyError as e:
            print(f"Error creating task: {e}")
            return None

    @classmethod
    async def get(cls, task_id: str) -> Optional['VideoTask']:
        async with async_session() as session:
            return await session.get(cls, task_id)
    
    @classmethod
    async def update(cls, task_id: str, **kwargs) -> Optional['VideoTask']:
        async with async_session() as session:
            task = await session.get(cls, task_id)
            if task:
                for key, value in kwargs.items():
                    setattr(task, key, value)
                await session.commit()
                await session.refresh(task)
            return task

    @classmethod
    async def delete(cls, task_id: str) -> bool:
        async with async_session() as session:
            task = await session.get(cls, task_id)
            if task:
                await session.delete(task)
                await session.commit()
                return True
            return False

    @classmethod
    async def list(cls, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> list['VideoTask']:
        async with async_session() as session:
            query = select(cls).limit(limit).offset(offset)
            if status:
                query = query.filter(cls.status == status)
            result = await session.execute(query)
            return result.scalars().all()

    async def save(self) -> None:
        async with async_session() as session:
            session.add(self)
            await session.commit()
            await session.refresh(self)