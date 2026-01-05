"""
Pydantic models for the appointment scheduling system.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Provider Models
class Provider(BaseModel):
    """Healthcare provider model."""
    id: str
    name: str
    specialty: str
    experience_years: int = Field(ge=0)
    rating: float = Field(ge=0.0, le=5.0)
    location: str


class Schedule(BaseModel):
    """Schedule model for provider availability."""
    provider_id: str
    date: str  # YYYY-MM-DD format
    available_slots: List[str]  # List of time slots like "09:00", "10:00"


# Appointment Models
class AppointmentCreate(BaseModel):
    """Request model for creating an appointment."""
    patient_name: str
    provider_id: str
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM format
    reason: Optional[str] = None


class Appointment(BaseModel):
    """Appointment model."""
    id: str
    patient_name: str
    provider_id: str
    provider_name: str
    date: str
    time: str
    location: str
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Conversation Models
class ConversationMessage(BaseModel):
    """A single message in a conversation."""
    role: str  # "user", "assistant", or "system"
    content: str


class ConversationRequest(BaseModel):
    """Request model for conversation endpoint."""
    message: str
    conversation_id: Optional[str] = None


class ConversationResponse(BaseModel):
    """Response model for conversation endpoint."""
    response: str
    conversation_id: str
    state: str  # Current conversation state
    suggested_actions: Optional[List[str]] = None


# LLM Tool Response Models
class ProviderMatch(BaseModel):
    """Result of provider matching."""
    provider_id: str
    provider_name: str
    specialty: str
    match_reason: str
    confidence: float = Field(ge=0.0, le=1.0)


class AvailabilityResult(BaseModel):
    """Result of availability check."""
    provider_id: str
    available_dates: List[str]
    available_slots: dict  # date -> list of time slots


class AppointmentConfirmation(BaseModel):
    """Confirmation of appointment creation."""
    appointment_id: str
    patient_name: str
    provider_name: str
    date: str
    time: str
    location: str
    ics_file: Optional[str] = None  # Base64 encoded .ics file
