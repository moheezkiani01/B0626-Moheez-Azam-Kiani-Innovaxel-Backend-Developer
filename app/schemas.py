from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class EventCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    total_seats: int = Field(..., gt=0)
    event_date: datetime

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Event name cannot be empty")
        return value


class EventResponse(BaseModel):
    id: int
    name: str
    total_seats: int
    event_date: str
    available_seats: int
    total_registrations: int


class RegistrationCreate(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=100)
    event_id: int = Field(..., gt=0)

    @field_validator("user_name")
    @classmethod
    def clean_user_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("User name cannot be empty")
        return value


class RegistrationCancel(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=100)
    event_id: int = Field(..., gt=0)

    @field_validator("user_name")
    @classmethod
    def clean_user_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("User name cannot be empty")
        return value
