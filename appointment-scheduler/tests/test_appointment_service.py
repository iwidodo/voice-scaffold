"""
Tests for appointment service.
"""
import pytest
from datetime import datetime
from backend.models.schemas import AppointmentCreate
from backend.services.appointment_service import (
    create_appointment,
    create_appointment_with_ics,
    generate_ics_file,
    get_appointment
)
from backend.database.schedules import clear_schedule_cache, get_provider_schedule


@pytest.fixture(autouse=True)
def reset_schedules():
    """Reset schedule cache before each test."""
    clear_schedule_cache()
    yield
    clear_schedule_cache()


def get_available_date_and_time(provider_id: str):
    """Helper to get an available date and time for testing."""
    schedules = get_provider_schedule(provider_id, days_ahead=14)
    for schedule in schedules:
        if schedule.available_slots:
            return schedule.date, schedule.available_slots[0]
    raise ValueError(f"No available slots found for provider {provider_id}")


def test_create_appointment():
    """Test creating an appointment."""
    date, time = get_available_date_and_time("p001")
    
    appointment_data = AppointmentCreate(
        patient_name="John Doe",
        provider_id="p001",
        date=date,
        time=time,
        reason="Skin checkup"
    )
    
    appointment = create_appointment(appointment_data)
    assert appointment is not None
    assert appointment.patient_name == "John Doe"
    assert appointment.provider_id == "p001"
    assert appointment.date == date
    assert appointment.time == time
    assert appointment.provider_name  # Should be populated from provider data


def test_create_appointment_with_invalid_provider():
    """Test creating appointment with nonexistent provider."""
    appointment_data = AppointmentCreate(
        patient_name="John Doe",
        provider_id="invalid_id",
        date="2026-01-15",
        time="10:00"
    )
    
    appointment = create_appointment(appointment_data)
    assert appointment is None


def test_generate_ics_file():
    """Test generating .ics file."""
    date, time = get_available_date_and_time("p001")
    
    appointment_data = AppointmentCreate(
        patient_name="Jane Smith",
        provider_id="p001",
        date=date,
        time=time,
        reason="Follow-up"
    )
    
    appointment = create_appointment(appointment_data)
    assert appointment is not None
    
    ics_bytes = generate_ics_file(appointment)
    assert ics_bytes
    assert b"BEGIN:VCALENDAR" in ics_bytes
    assert b"BEGIN:VEVENT" in ics_bytes
    assert appointment.provider_name.encode() in ics_bytes
    assert b"Jane Smith" in ics_bytes


def test_create_appointment_with_ics():
    """Test creating appointment and generating .ics in one call."""
    date, time = get_available_date_and_time("p002")
    
    appointment_data = AppointmentCreate(
        patient_name="Bob Johnson",
        provider_id="p002",
        date=date,
        time=time,
        reason="Consultation"
    )
    
    confirmation = create_appointment_with_ics(appointment_data)
    assert confirmation is not None
    assert confirmation.appointment_id
    assert confirmation.patient_name == "Bob Johnson"
    assert confirmation.ics_file  # Should be base64 encoded


def test_get_appointment():
    """Test retrieving an appointment."""
    date, time = get_available_date_and_time("p003")
    
    appointment_data = AppointmentCreate(
        patient_name="Alice Brown",
        provider_id="p003",
        date=date,
        time=time
    )
    
    appointment = create_appointment(appointment_data)
    assert appointment is not None
    
    retrieved = get_appointment(appointment.id)
    assert retrieved is not None
    assert retrieved.id == appointment.id
    assert retrieved.patient_name == "Alice Brown"


def test_get_nonexistent_appointment():
    """Test retrieving nonexistent appointment."""
    result = get_appointment("nonexistent_id")
    assert result is None


def test_appointment_timestamps():
    """Test that appointments have timestamps."""
    date, time = get_available_date_and_time("p001")
    
    appointment_data = AppointmentCreate(
        patient_name="Test User",
        provider_id="p001",
        date=date,
        time=time
    )
    
    appointment = create_appointment(appointment_data)
    assert appointment is not None
    assert appointment.created_at
    assert isinstance(appointment.created_at, datetime)
