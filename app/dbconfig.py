from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.dbconfig import settings

engine = create_async_engine(
    settings.DB_URL,
    connect_args={"statement_cache_size": 0},  # Disable asyncpg prepared stmt cache
    pool_pre_ping=True,                        # Avoid stale connections
    pool_size=5,                               # Keep small pool size for Render
    max_overflow=0
)

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
