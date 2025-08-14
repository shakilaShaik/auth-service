from fastapi import FastAPI
from app.routes import router
from app.models import Base
from app.dbconnect import engine
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Auth Service", lifespan=lifespan)
frotnend_origin=os.getenv("ALLOWED_ORIGINS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=   frotnend_origin, 
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True, 
)
app.include_router(router)
