"""
Appointment API endpoints.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from typing import List
import base64

from backend.models.schemas import (
    AppointmentCreate,
    Appointment,
    AppointmentConfirmation
)
from backend.services.appointment_service import (
    create_appointment_with_ics,
    get_appointment,
    get_all_appointments
)
from backend.database.providers import get_provider_by_id

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentConfirmation)
async def create_new_appointment(appointment_data: AppointmentCreate):
    """
    Create a new appointment and generate .ics file.
    
    Args:
        appointment_data: Appointment details
        
    Returns:
        AppointmentConfirmation with .ics file
    """
    # Validate provider exists
    provider = get_provider_by_id(appointment_data.provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Create appointment
    confirmation = create_appointment_with_ics(appointment_data)
    if not confirmation:
        raise HTTPException(
            status_code=400,
            detail="Failed to create appointment. The time slot may no longer be available."
        )
    
    return confirmation


@router.get("/{appointment_id}", response_model=Appointment)
async def get_appointment_by_id(appointment_id: str):
    """
    Get an appointment by ID.
    
    Args:
        appointment_id: Appointment ID
        
    Returns:
        Appointment details
    """
    appointment = get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.get("/", response_model=List[Appointment])
async def list_appointments():
    """
    List all appointments.
    
    Returns:
        List of all appointments
    """
    return get_all_appointments()


@router.get("/{appointment_id}/ics")
async def download_ics_file(appointment_id: str):
    """
    Download .ics file for an appointment.
    
    Args:
        appointment_id: Appointment ID
        
    Returns:
        .ics file as downloadable attachment
    """
    appointment = get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Generate fresh .ics file
    from backend.services.appointment_service import generate_ics_file
    ics_bytes = generate_ics_file(appointment)
    
    return Response(
        content=ics_bytes,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=appointment_{appointment_id}.ics"
        }
    )
