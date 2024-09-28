import asyncio
import sys
import os
from app.core.logging import logger

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.db.init_db import init_db

async def run():
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialization completed.")

if __name__ == "__main__":
    asyncio.run(run())