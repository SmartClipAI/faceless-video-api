from app.db.base import Base
from app.db.session import engine, async_session
from app.core.config import settings
from app.core.security import get_password_hash
from sqlalchemy.future import select
from app.models.user import User  # Add this import at the top of the file
from app.core.logging import logger

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    if settings.ADMIN_USERNAME and settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        async with async_session() as session:
            result = await session.execute(select(User).where(User.username == settings.ADMIN_USERNAME))
            user = result.scalars().first()
            if not user:
                admin_user = User(
                    username=settings.ADMIN_USERNAME,
                    email=settings.ADMIN_EMAIL,
                    hashed_password=get_password_hash(settings.ADMIN_PASSWORD),  
                    is_active=True,
                    is_admin=True
                )
                session.add(admin_user)
                await session.commit()
                logger.info(f"Created admin user: {admin_user.username}")
            else:
                logger.info(f"Admin user already exists: {user.username}")
    else:
        logger.warning("Admin credentials not provided. Skipping admin user creation.")