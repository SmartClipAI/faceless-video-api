from sqlalchemy import Column, String, Float, DateTime, Text, select, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import async_session
from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
from app.db.base_class import Base  # Import Base from base_class, not from base
from app.core.logging import logger



class VideoTask(Base):
    __tablename__ = "video_tasks"

    id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=True)
    story_topic = Column(String, nullable=False)
    art_style = Column(String, nullable=False)
    duration = Column(Enum('short', 'long', name='duration'), nullable=False)
    voice_name = Column(Enum('echo', 'alloy', 'onyx', 'fable', 'nova', 'shimmer', name='voice_name'), nullable=False)
    language = Column(Enum('english', 'czech', 'danish', 'dutch', 'french', 'german', 'greek', 'hindi', 'indonesian', 'italian', 'japanese', 'norwegian', 'polish', 'portuguese', 'russian', 'spanish', 'swedish', 'turkish', 'ukrainian', name='language'), nullable=False)
    story_title = Column(Text)
    story_description = Column(Text)
    story_text = Column(Text)
    status = Column(Enum('queued', 'processing', 'completed', 'failed', name='status'), nullable=False)
    error_message = Column(Text)
    progress = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    images = relationship("Image", back_populates="task")

    @classmethod
    async def create(cls, **kwargs) -> Optional['VideoTask']:
        try:
            async with async_session() as session:
                task = cls(**kwargs)
                session.add(task)
                await session.commit()
                await session.refresh(task)
                logger.info(f"VideoTask with task_id {kwargs.get('id')} created successfully")
            return task
        except SQLAlchemyError as e:
            logger.error(f"Error creating VideoTask: {e}")
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
                logger.info(f"VideoTask with task_id {task_id} updated successfully")
            else:
                logger.error(f"VideoTask with task_id {task_id} not found")
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
    async def list(cls, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List['VideoTask']:
        async with async_session() as session:
            query = select(cls).limit(limit).offset(offset)
            if status:
                query = query.filter(cls.status == status)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_by_status(cls, status: str) -> List['VideoTask']:
        async with async_session() as session:
            query = select(cls).filter(cls.status == status)
            result = await session.execute(query)
            return result.scalars().all()