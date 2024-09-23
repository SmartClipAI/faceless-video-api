from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from app.db.base_class import Base
from app.db.session import async_session
from app.core.logging import logger

class Image(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("image_tasks.id"), nullable=False)
    url = Column(String)
    subtitles = Column(Text)
    status = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    task = relationship("ImageTask", back_populates="images")

    @classmethod
    async def create(cls, **kwargs) -> Optional['Image']:
        try:
            async with async_session() as session:
                image = cls(**kwargs)
                session.add(image)
                await session.commit()
                await session.refresh(image)
            return image
        except SQLAlchemyError as e:
            logger.error(f"Error creating image: {e}")
            return None

    @classmethod
    async def get(cls, image_id: str) -> Optional['Image']:
        async with async_session() as session:
            return await session.get(cls, image_id)

    @classmethod
    async def update(cls, image_id: str, **kwargs) -> Optional['Image']:
        async with async_session() as session:
            image = await session.get(cls, image_id)
            if image:
                for key, value in kwargs.items():
                    setattr(image, key, value)
                await session.commit()
                await session.refresh(image)
            return image

    @classmethod
    async def delete(cls, image_id: str) -> bool:
        async with async_session() as session:
            image = await session.get(cls, image_id)
            if image:
                await session.delete(image)
                await session.commit()
                return True
            return False

    @classmethod
    async def list_by_task(cls, task_id: str, limit: int = 100, offset: int = 0) -> List['Image']:
        async with async_session() as session:
            query = select(cls).filter(cls.task_id == task_id).limit(limit).offset(offset)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_by_task_and_status(cls, task_id: str, status: str) -> List['Image']:
        async with async_session() as session:
            query = select(cls).filter(cls.task_id == task_id, cls.status == status)
            result = await session.execute(query)
            return result.scalars().all()