"""
app/seed.py
───────────
Programmatic seed script. Reads seed.sql and executes it against the database.
Can be run as: python -m app.seed
Only inserts data if the test user doesn't already exist (idempotent).
"""

import asyncio
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def run_seed():
    """Execute seed.sql against the database."""
    engine = create_async_engine(settings.database_url, echo=False)

    seed_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "seed.sql")

    if not os.path.exists(seed_path):
        print("seed.sql not found, skipping seed")
        return

    with open(seed_path, "r") as f:
        sql = f.read()

    async with engine.begin() as conn:
        # Execute each statement separately
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement and not statement.startswith("--"):
                await conn.execute(text(statement))

    await engine.dispose()
    print("Seed data inserted successfully")


if __name__ == "__main__":
    asyncio.run(run_seed())
