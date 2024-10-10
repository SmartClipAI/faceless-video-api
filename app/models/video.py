# from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum
# from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy.exc import SQLAlchemyError
# from typing import Optional, List
# from app.db.base_class import Base
# from app.db.session import async_session
# from app.core.logging import logger


# class Video(Base):
#     __tablename__ = "videos"

#     id = Column(String, primary_key=True, index=True)
#     task_id = Column(String, ForeignKey("video_tasks.id"), nullable=False, index=True)
#     url = Column(String)
#     story_topic = Column(String, nullable=False)
#     story_text = Column(Text, nullable=False)
#     story_title = Column(Text, nullable=False)
#     story_description = Column(Text, nullable=False)
#     art_style = Column(String, nullable=False)
#     duration = Column(Enum('short', 'long', name='duration'), nullable=False)
#     language = Column(Enum('english', 'czech', 'danish', 'dutch', 'french', 'german', 'greek', 'hindi', 'indonesian', 'italian', 'japanese', 'norwegian', 'polish', 'portuguese', 'russian', 'spanish', 'swedish', 'turkish', 'ukrainian', name='language'), nullable=False)
#     voice_name = Column(Enum('echo', 'alloy', 'onyx', 'fable', 'nova', 'shimmer', name='voice_name'), nullable=False)
#     error_message = Column(Text)
#     status = Column(Enum('queued', 'processing', 'completed', 'failed', name='video_status'), nullable=False, index=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())

#     task = relationship("VideoTask", back_populates="video")

#     @classmethod
#     async def create(cls, **kwargs) -> Optional['Video']:
#         try:
#             async with async_session() as session:
#                 video = cls(**kwargs)
#                 session.add(video)
#                 await session.commit()
#                 await session.refresh(video)
#                 logger.info(f"Video with task_id {kwargs.get('task_id')} created successfully")
#                 return video
#         except SQLAlchemyError as e:
#             logger.error(f"Error creating video: {str(e)}")
#             return None

#     @classmethod
#     async def get(cls, video_id: str) -> Optional['Video']:
#         async with async_session() as session:
#             return await session.get(cls, video_id)

#     @classmethod
#     async def update(cls, video_id: str, **kwargs) -> Optional['Video']:
#         async with async_session() as session:
#             video = await session.get(cls, video_id)
#             if video:
#                 for key, value in kwargs.items():
#                     setattr(video, key, value)
#                 await session.commit()
#                 await session.refresh(video)
#             return video

#     @classmethod
#     async def delete(cls, video_id: str) -> bool:
#         async with async_session() as session:
#             video = await session.get(cls, video_id)
#             if video:
#                 await session.delete(video)
#                 await session.commit()
#                 return True
#             return False

#     @classmethod
#     async def list_by_task(cls, task_id: str, limit: int = 100, offset: int = 0) -> List['Video']:
#         async with async_session() as session:
#             query = select(cls).filter(cls.task_id == task_id).limit(limit).offset(offset)
#             result = await session.execute(query)
#             return result.scalars().all()

#     @classmethod
#     async def get_by_task_and_status(cls, task_id: str, status: str) -> List['Video']:
#         async with async_session() as session:
#             query = select(cls).filter(cls.task_id == task_id, cls.status == status)
#             result = await session.execute(query)
#             return result.scalars().all()