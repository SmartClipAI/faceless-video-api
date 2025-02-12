import asyncio
import sys
import os
from app.core.logging import logger
from dotenv import load_dotenv

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Load environment variables from .env file
load_dotenv()

from app.db.init_db import init_db

async def run():
    print("\033[91m" + "WARNING! This will delete all data in your database!" + "\033[0m")
    print("\033[91m" + "All tables will be dropped and recreated." + "\033[0m")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("\033[91m" + "ERROR: DATABASE_URL environment variable is not set!" + "\033[0m")
        print("Please set it in your .env file, example:")
        print("DATABASE_URL=postgresql://username:password@localhost:5432/database_name")
        return
    
    print("\033[93m" + "Target Database:", database_url + "\033[0m")
    
    confirmation = input("\nAre you sure you want to continue? [y/N]: ")
    if confirmation.lower() != 'y':
        print("Database initialization cancelled.")
        return

    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialization completed.")

if __name__ == "__main__":
    asyncio.run(run())