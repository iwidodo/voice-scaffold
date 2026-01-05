"""
Appointment API endpoints.
"""
import logging
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

logger = logging.getLogger(__name__)
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
    logger.info(f"[appointments.py.create_new_appointment] Creating appointment for patient: {appointment_data.patient_name}, provider: {appointment_data.provider_id}")
    
    # Validate provider exists
    provider = get_provider_by_id(appointment_data.provider_id)
    if not provider:
        logger.error(f"[appointments.py.create_new_appointment] Provider not found: {appointment_data.provider_id}")
        raise HTTPException(status_code=404, detail="Provider not found")
    
    logger.debug(f"[appointments.py.create_new_appointment] Provider validated: {provider.name}")
    
    # Create appointment
    confirmation = create_appointment_with_ics(appointment_data)
    if not confirmation:
        logger.error(f"[appointments.py.create_new_appointment] Failed to create appointment for provider: {appointment_data.provider_id}, date: {appointment_data.date}, time: {appointment_data.time}")
        raise HTTPException(
            status_code=400,
            detail="Failed to create appointment. The time slot may no longer be available."
        )
    
    logger.info(f"[appointments.py.create_new_appointment] Appointment created successfully: {confirmation.appointment_id}")
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
    logger.info(f"[appointments.py.get_appointment_by_id] Fetching appointment: {appointment_id}")
    
    appointment = get_appointment(appointment_id)
    if not appointment:
        logger.warning(f"[appointments.py.get_appointment_by_id] Appointment not found: {appointment_id}")
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    logger.debug(f"[appointments.py.get_appointment_by_id] Appointment retrieved: {appointment.patient_name} with {appointment.provider_name}")
    return appointment


@router.get("/", response_model=List[Appointment])
async def list_appointments():
    """
    List all appointments.
    
    Returns:
        List of all appointments
    """
    logger.info("[appointments.py.list_appointments] Fetching all appointments")
    appointments = get_all_appointments()
    logger.debug(f"[appointments.py.list_appointments] Retrieved {len(appointments)} appointments")
    return appointments


@router.get("/{appointment_id}/ics")
async def download_ics_file(appointment_id: str):
    """
    Download .ics file for an appointment.
    
    Args:
        appointment_id: Appointment ID
        
    Returns:
        .ics file as downloadable attachment
    """
    logger.info(f"[appointments.py.download_ics_file] Downloading ICS file for appointment: {appointment_id}")
    
    appointment = get_appointment(appointment_id)
    if not appointment:
        logger.warning(f"[appointments.py.download_ics_file] Appointment not found: {appointment_id}")
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Generate fresh .ics file
    from backend.services.appointment_service import generate_ics_file
    ics_bytes = generate_ics_file(appointment)
    
    logger.debug(f"[appointments.py.download_ics_file] Generated ICS file for appointment: {appointment_id}")
    
    return Response(
        content=ics_bytes,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=appointment_{appointment_id}.ics"
        }
    )
