from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.dbconfig import settings  # no load_dotenv here

# Create async engine with PgBouncer-safe config
engine = create_async_engine(
    settings.DB_URL,
   echo=True,
    pool_pre_ping=True 
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base model
Base = declarative_base()

# Dependency for FastAPI routes
async def get_db():
    async with SessionLocal() as session:
        yield session
