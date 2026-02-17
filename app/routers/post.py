from fastapi  import Depends, status, HTTPException, Query, APIRouter
from typing import Annotated, Optional
from sqlmodel import  select
from ..database import SessionDep
from .. import models, schemas, oauth2
from sqlalchemy import func



router =  APIRouter(
    prefix="/posts",
    tags=['Posts']
)

#@router.get("/", response_model=list[schemas.Post])
@router.get("/", response_model=list[schemas.PostOut])
def get_post(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=10)] = 10,
    search: Optional[str] = ""
):   
    
    statement = (
        select(
            models.Post,
            func.count(models.Votes.post_id).label("votes")
        )
        .join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .offset(offset)
        .limit(limit)
    )
    if search:
        statement = statement.where(models.Post.title.contains(search))

    results = session.exec(statement).all()
    return [
        schemas.PostOut(post=post, votes=votes)
        for post, votes in results
    ]




@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, session: SessionDep, current_user: int = Depends(oauth2.get_current_user)):
    print(current_user.email)
    db_post = models.Post.model_validate(
    post,
    update={"owner_id": current_user.id})
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int,
    session: SessionDep,
    current_user: int = Depends(oauth2.get_current_user),
):
    statement = (
        select(
            models.Post,
            func.count(models.Votes.post_id).label("votes")
        )
        .join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True)
        .where(models.Post.id == id)
        .group_by(models.Post.id)
    )

    result = session.exec(statement).first()

    if not result:
        raise HTTPException(status_code=404, detail="Post not found")

    post, votes = result

    return schemas.PostOut(post=post, votes=votes)




@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, session: SessionDep, current_user: int = Depends(oauth2.get_current_user)):
    post = session.get(models.Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to perform requested action")
    session.delete(post)
    session.commit()
    return {"ok": True}


@router.put("/{id}", response_model=schemas.Post)
def update_post(id:int, updated_data: schemas.PostCreate, session: SessionDep, current_user: int = Depends(oauth2.get_current_user)):
    post = session.get(models.Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to perform requested action")    
    post.title = updated_data.title
    post.content = updated_data.content 
    post.published = updated_data.published
    session.add(post)
    session.commit()
    session.refresh(post)    
    return post