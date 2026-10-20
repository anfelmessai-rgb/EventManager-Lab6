import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ==========================================
# Event Schemas
# ==========================================
class EventBase(BaseModel):
    title: str = Field(..., min_length=3, description="Title must be >= 3 characters")
    location: str
    capacity: int = Field(..., ge=1, le=10000, description="Capacity must be between 1 and 10000 inclusive")
    description: Optional[str] = None
    date: datetime.date = Field(default_factory=datetime.date.today)


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3)
    location: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=1, le=10000)
    description: Optional[str] = None
    date: Optional[datetime.date] = None


class Event(EventBase):
    id: int

    class Config:
        from_attributes = True


# ==========================================
# Participant Schemas
# ==========================================
class ParticipantBase(BaseModel):
    name: str = Field(..., min_length=2, description="Name must be >= 2 characters")
    email: EmailStr


class ParticipantCreate(ParticipantBase):
    pass


class Participant(ParticipantBase):
    id: int
    event_id: Optional[int] = None

    class Config:
        from_attributes = True


# ==========================================
# Registration Schemas
# ==========================================
class RegistrationBase(BaseModel):
    event_id: int
    participant_id: int


class RegistrationCreate(RegistrationBase):
    pass


class Registration(RegistrationBase):
    id: int

    class Config:
        from_attributes = True