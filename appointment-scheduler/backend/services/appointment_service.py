"""
Appointment service for creating appointments and generating .ics files.
"""
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional
from icalendar import Calendar, Event
from backend.models.schemas import Appointment, AppointmentCreate, AppointmentConfirmation
from backend.database.providers import get_provider_by_id
from backend.database.schedules import book_slot

logger = logging.getLogger(__name__)

# In-memory appointment storage (would be a database in production)
_APPOINTMENTS_DB = {}


def create_appointment(appointment_data: AppointmentCreate) -> Optional[Appointment]:
    """
    Create a new appointment.
    
    Args:
        appointment_data: Appointment creation data
        
    Returns:
        Created Appointment object or None if provider not found
    """
    logger.info(f"[appointment_service.py.create_appointment] Creating appointment for patient: {appointment_data.patient_name}, provider: {appointment_data.provider_id}")
    
    provider = get_provider_by_id(appointment_data.provider_id)
    if not provider:
        logger.error(f"[appointment_service.py.create_appointment] Provider not found: {appointment_data.provider_id}")
        return None
    
    logger.debug(f"[appointment_service.py.create_appointment] Provider found: {provider.name}")
    
    # Book the slot
    success = book_slot(
        appointment_data.provider_id,
        appointment_data.date,
        appointment_data.time
    )
    
    if not success:
        logger.warning(f"[appointment_service.py.create_appointment] Failed to book slot for {appointment_data.date} at {appointment_data.time}")
        return None
    
    logger.debug(f"[appointment_service.py.create_appointment] Slot booked successfully")
    
    # Create appointment
    appointment_id = str(uuid.uuid4())
    appointment = Appointment(
        id=appointment_id,
        patient_name=appointment_data.patient_name,
        provider_id=appointment_data.provider_id,
        provider_name=provider.name,
        date=appointment_data.date,
        time=appointment_data.time,
        location=provider.location,
        reason=appointment_data.reason
    )
    
    _APPOINTMENTS_DB[appointment_id] = appointment
    logger.info(f"[appointment_service.py.create_appointment] Appointment created successfully: {appointment_id}")
    
    return appointment


def generate_ics_file(appointment: Appointment) -> bytes:
    """
    Generate an iCalendar (.ics) file for an appointment.
    
    Args:
        appointment: Appointment object
        
    Returns:
        .ics file content as bytes
    """
    logger.info(f"[appointment_service.py.generate_ics_file] Generating ICS file for appointment: {appointment.id}")
    
    cal = Calendar()
    cal.add('prodid', '-//Appointment Scheduler//EN')
    cal.add('version', '2.0')
    
    event = Event()
    event.add('summary', f'Appointment with {appointment.provider_name}')
    event.add('location', appointment.location)
    
    # Parse date and time
    date_obj = datetime.strptime(appointment.date, "%Y-%m-%d")
    time_obj = datetime.strptime(appointment.time, "%H:%M").time()
    start_datetime = datetime.combine(date_obj, time_obj)
    
    event.add('dtstart', start_datetime)
    
    # Assume 30-minute appointments - use timedelta for proper calculation
    end_datetime = start_datetime + timedelta(minutes=30)
    
    event.add('dtend', end_datetime)
    event.add('dtstamp', datetime.now())
    
    # Add description
    description = f"Patient: {appointment.patient_name}\n"
    description += f"Provider: {appointment.provider_name}\n"
    if appointment.reason:
        description += f"Reason: {appointment.reason}\n"
    event.add('description', description)
    
    event.add('uid', appointment.id)
    
    cal.add_component(event)
    
    ics_bytes = cal.to_ical()
    logger.debug(f"[appointment_service.py.generate_ics_file] ICS file generated successfully (size: {len(ics_bytes)} bytes)")
    
    return ics_bytes


def create_appointment_with_ics(
    appointment_data: AppointmentCreate
) -> Optional[AppointmentConfirmation]:
    """
    Create an appointment and generate .ics file.
    
    Args:
        appointment_data: Appointment creation data
        
    Returns:
        AppointmentConfirmation with .ics file or None if creation failed
    """
    logger.info(f"[appointment_service.py.create_appointment_with_ics] Creating appointment with ICS for patient: {appointment_data.patient_name}")
    
    appointment = create_appointment(appointment_data)
    if not appointment:
        logger.error(f"[appointment_service.py.create_appointment_with_ics] Failed to create appointment")
        return None
    
    ics_bytes = generate_ics_file(appointment)
    
    # Convert to base64 for JSON transmission
    import base64
    ics_base64 = base64.b64encode(ics_bytes).decode('utf-8')
    
    logger.info(f"[appointment_service.py.create_appointment_with_ics] Appointment with ICS created successfully: {appointment.id}")
    
    return AppointmentConfirmation(
        appointment_id=appointment.id,
        patient_name=appointment.patient_name,
        provider_name=appointment.provider_name,
        date=appointment.date,
        time=appointment.time,
        location=appointment.location,
        ics_file=ics_base64
    )


def get_appointment(appointment_id: str) -> Optional[Appointment]:
    """Get an appointment by ID."""
    logger.debug(f"[appointment_service.py.get_appointment] Retrieving appointment: {appointment_id}")
    appointment = _APPOINTMENTS_DB.get(appointment_id)
    
    if appointment:
        logger.debug(f"[appointment_service.py.get_appointment] Appointment found: {appointment_id}")
    else:
        logger.warning(f"[appointment_service.py.get_appointment] Appointment not found: {appointment_id}")
    
    return appointment


def get_all_appointments() -> list:
    """Get all appointments."""
    logger.debug(f"[appointment_service.py.get_all_appointments] Retrieving all appointments (count: {len(_APPOINTMENTS_DB)})")
    return list(_APPOINTMENTS_DB.values())
