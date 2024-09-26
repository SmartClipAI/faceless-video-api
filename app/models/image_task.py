from sqlalchemy import Column, String, Float, DateTime, Text, select, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import async_session
from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
from app.db.base_class import Base  # Import Base from base_class, not from base
from app.core.logging import logger


class ImageTask(Base):
    __tablename__ = "image_tasks"

    id = Column(String, primary_key=True, index=True)
    story_topic = Column(String, nullable=False)
    art_style = Column(String, nullable=False)
    status = Column(Enum('queued', 'processing', 'completed', 'failed', name='task_status'), nullable=False, index=True)
    progress = Column(Float, default=0.0)
    story_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    images = relationship("Image", back_populates="task")

    @classmethod
    async def create(cls, **kwargs) -> Optional['ImageTask']:
        try:
            async with async_session() as session:
                task = cls(**kwargs)
                session.add(task)
                await session.commit()
                await session.refresh(task)
            return task
        except SQLAlchemyError as e:
            logger.error(f"Error creating task: {e}")
            return None

    @classmethod
    async def get(cls, task_id: str) -> Optional['ImageTask']:
        async with async_session() as session:
            return await session.get(cls, task_id)

    @classmethod
    async def update(cls, task_id: str, **kwargs) -> Optional['ImageTask']:
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
    async def list(cls, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List['ImageTask']:
        async with async_session() as session:
            query = select(cls).limit(limit).offset(offset)
            if status:
                query = query.filter(cls.status == status)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_by_status(cls, status: str) -> List['ImageTask']:
        async with async_session() as session:
            query = select(cls).filter(cls.status == status)
            result = await session.execute(query)
            return result.scalars().all()