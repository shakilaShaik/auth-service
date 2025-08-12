from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserRegister(UserBase):
    name: str
    password: str


class UserLogin(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    user_id: int
    exp: int
    type: str
    jti: str | None = None
