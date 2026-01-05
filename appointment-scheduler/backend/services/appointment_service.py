"""
Appointment service for creating appointments and generating .ics files.
"""
import uuid
from datetime import datetime
from typing import Optional
from icalendar import Calendar, Event
from backend.models.schemas import Appointment, AppointmentCreate, AppointmentConfirmation
from backend.database.providers import get_provider_by_id
from backend.database.schedules import book_slot


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
    provider = get_provider_by_id(appointment_data.provider_id)
    if not provider:
        return None
    
    # Book the slot
    success = book_slot(
        appointment_data.provider_id,
        appointment_data.date,
        appointment_data.time
    )
    
    if not success:
        return None
    
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
    return appointment


def generate_ics_file(appointment: Appointment) -> bytes:
    """
    Generate an iCalendar (.ics) file for an appointment.
    
    Args:
        appointment: Appointment object
        
    Returns:
        .ics file content as bytes
    """
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
    
    # Assume 30-minute appointments
    end_datetime = start_datetime.replace(
        minute=start_datetime.minute + 30 if start_datetime.minute < 30 else 0,
        hour=start_datetime.hour if start_datetime.minute < 30 else start_datetime.hour + 1
    )
    
    event.add('dtstart', start_datetime)
    event.add('dtend', end_datetime)
    event.add('dtstamp', datetime.utcnow())
    
    # Add description
    description = f"Patient: {appointment.patient_name}\n"
    description += f"Provider: {appointment.provider_name}\n"
    if appointment.reason:
        description += f"Reason: {appointment.reason}\n"
    event.add('description', description)
    
    event.add('uid', appointment.id)
    
    cal.add_component(event)
    
    return cal.to_ical()


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
    appointment = create_appointment(appointment_data)
    if not appointment:
        return None
    
    ics_bytes = generate_ics_file(appointment)
    
    # Convert to base64 for JSON transmission
    import base64
    ics_base64 = base64.b64encode(ics_bytes).decode('utf-8')
    
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
    return _APPOINTMENTS_DB.get(appointment_id)


def get_all_appointments() -> list:
    """Get all appointments."""
    return list(_APPOINTMENTS_DB.values())
