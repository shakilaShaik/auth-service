from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.dbconnect import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    refresh_token_expires = Column(
        DateTime(timezone=True), nullable=True
    )  # Changed to timezone-aware
    token_version = Column(String, nullable=False, default=lambda: str(uuid.uuid4()))
