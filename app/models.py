from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from sqlalchemy import Column, DateTime, text
from datetime import datetime


class Post(SQLModel, table= True):
  __tablename__= "post"

  id: Optional[int] = Field(default=None,primary_key=True)
  title: str
  content: str
  published: bool = Field(
    default=True,
    sa_column_kwargs={"server_default": text("true")})
  created_at: datetime | None = Field(
    default=None,
    sa_column=Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False
    ))
  owner_id: int | None = Field(
    default=None,
    foreign_key="users.id",
    ondelete="CASCADE"
  )
    
  owner: Optional["User"] = Relationship(back_populates="posts")
  

class User(SQLModel, table= True):
  __tablename__= "users"
  id: Optional[int] = Field(default=None,primary_key=True)
  email: str = Field(index=True, unique=True)
  password: str 
  created_at: datetime | None = Field(
    default=None,
    sa_column=Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False
    ))  
  posts: list["Post"] = Relationship(back_populates="owner", cascade_delete=True)


class Votes(SQLModel, table= True):
  __tablename__ = "votes"
  user_id: int = Field(default=None,foreign_key= "users.id", primary_key=True, ondelete="CASCADE")
  post_id: int = Field(default=None,foreign_key= "post.id", primary_key=True, ondelete="CASCADE")


