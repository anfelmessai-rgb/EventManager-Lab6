from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Event
from ..schemas import Event as EventSchema
from ..schemas import EventCreate, EventUpdate


router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


# =======================================================
# Pure Helper Functions (Required for Lab 2 Unit Tests)
# =======================================================
def filter_events_by_location(events: list, location: str) -> list:
    """Pure search helper function: returns case-insensitive location matches."""
    return [
        e for e in events
        if location.lower() in (e["location"] if isinstance(e, dict) else e.location).lower()
    ]


def filter_events_by_title(events: list, title: str) -> list:
    """Pure search helper function: returns case-insensitive title matches."""
    return [
        e for e in events
        if title.lower() in (e["title"] if isinstance(e, dict) else e.title).lower()
    ]


# =======================================================
# Endpoints
# =======================================================
@router.post(
    "/",
    response_model=EventSchema,
    status_code=status.HTTP_201_CREATED
)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    if event.date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Event date cannot be in the past."
        )

    db_event = Event(**event.model_dump())

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event


@router.get(
    "/",
    response_model=list[EventSchema]
)
def list_events(
    title: str | None = Query(default=None),
    search: str | None = Query(default=None),
    location: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Lab 1 Challenge Solution:
    Combines both location and title/search filters together in the SQL query.
    """
    query = db.query(Event)

    if location:
        query = query.filter(Event.location.ilike(f"%{location}%"))

    # Supports both ?title= and ?search=
    keyword = title or search
    if keyword:
        query = query.filter(Event.title.ilike(f"%{keyword}%"))

    return query.order_by(Event.date).all()


@router.get(
    "/{event_id}",
    response_model=EventSchema
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found."
        )

    return event


@router.put(
    "/{event_id}",
    response_model=EventSchema
)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db)
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found."
        )

    if event_data.date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Event date cannot be in the past."
        )

    for key, value in event_data.model_dump().items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)

    return event


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found."
        )

    db.delete(event)
    db.commit()