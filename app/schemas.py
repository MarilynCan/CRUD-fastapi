from sqlmodel import SQLModel
from datetime import datetime
from pydantic import EmailStr
from typing import Optional


class UserCreate(SQLModel):
    email: EmailStr
    password: str

class User(UserCreate):
    id: int
    created_at : datetime


class UserOut(SQLModel):
    id: int
    email: EmailStr
    created_at : datetime


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class PostBase(SQLModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        from_attributes = True

class PostOut(SQLModel):
    post:Post
    votes: int

    class Config:
        from_attributes = True




class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    id: Optional[int] = None

class Vote(SQLModel):
    post_id: int
    dir: bool
    


