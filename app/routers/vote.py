from fastapi  import Depends, status, HTTPException, APIRouter
from sqlmodel import  select
from ..database import SessionDep
from .. import models, schemas, oauth2


router =  APIRouter(
    prefix="/vote",
    tags=['Vote']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, session: SessionDep, current_user: int = Depends(oauth2.get_current_user)):
  # Verificar que el post exista
  post = session.get(models.Post, vote.post_id)
  if not post:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail=f"Post with id: {vote.post_id} does not exit"
      )  
  # Buscar si ya existe el voto
  statement = select(models.Votes).where(
        models.Votes.post_id == vote.post_id,
        models.Votes.user_id == current_user.id
    )  
  found_vote = session.exec(statement).first()  

  # Agregar voto
  if vote.dir:
    if found_vote:
      raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                          detail=f"user {current_user.id} has already voted on post {vote.post_id}")
    new_vote = models.Votes(
            post_id=vote.post_id,
            user_id=current_user.id
        )
    session.add(new_vote)
    session.commit()
    return {"message": "successfully added vote"}   
  
  # QUITAR VOTO
  else:
    if not found_vote:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                          detail=f"Vote does not exist")
    session.delete(found_vote)
    session.commit()
    return {"message": "successfully deleted vote"}  
