from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Participant
from ..schemas import Participant as ParticipantSchema, ParticipantCreate

router = APIRouter(
    prefix="/participants",
    tags=["Participants"]
)


def has_available_capacity(current_count: int, max_capacity: int) -> bool:
    return current_count < max_capacity


def check_duplicate_registration(registered_ids: list, new_id: int):
    if new_id in registered_ids:
        raise ValueError(f"Participant with ID {new_id} is already registered.")


@router.post("/", response_model=ParticipantSchema, status_code=status.HTTP_201_CREATED)
def register_participant(participant: ParticipantCreate, db: Session = Depends(get_db)):
    db_participant = Participant(**participant.model_dump())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


@router.get("/", response_model=List[ParticipantSchema])
def list_participants(db: Session = Depends(get_db)):
    return db.query(Participant).all()