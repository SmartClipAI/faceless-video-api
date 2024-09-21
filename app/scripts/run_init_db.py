import asyncio
import sys
import os

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.db.init_db import init_db

async def run():
    print("Initializing database...")
    await init_db()
    print("Database initialization completed.")

if __name__ == "__main__":
    asyncio.run(run())