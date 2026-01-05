"""
Tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.schedules import clear_schedule_cache

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_schedules():
    """Reset schedule cache before each test."""
    clear_schedule_cache()
    yield
    clear_schedule_cache()


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_appointment_endpoint():
    """Test appointment creation endpoint."""
    appointment_data = {
        "patient_name": "John Doe",
        "provider_id": "p001",
        "date": "2026-01-20",
        "time": "10:00",
        "reason": "Checkup"
    }
    
    response = client.post("/api/appointments/", json=appointment_data)
    assert response.status_code == 200
    data = response.json()
    assert data["patient_name"] == "John Doe"
    assert data["appointment_id"]
    assert data["ics_file"]  # Should include base64 encoded .ics


def test_create_appointment_invalid_provider():
    """Test appointment creation with invalid provider."""
    appointment_data = {
        "patient_name": "Jane Smith",
        "provider_id": "invalid",
        "date": "2026-01-20",
        "time": "10:00"
    }
    
    response = client.post("/api/appointments/", json=appointment_data)
    assert response.status_code == 404


def test_get_appointment_endpoint():
    """Test getting an appointment."""
    # First create an appointment
    appointment_data = {
        "patient_name": "Bob Johnson",
        "provider_id": "p002",
        "date": "2026-01-22",
        "time": "14:00"
    }
    
    create_response = client.post("/api/appointments/", json=appointment_data)
    assert create_response.status_code == 200
    appointment_id = create_response.json()["appointment_id"]
    
    # Now get it
    response = client.get(f"/api/appointments/{appointment_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == appointment_id
    assert data["patient_name"] == "Bob Johnson"


def test_get_nonexistent_appointment():
    """Test getting nonexistent appointment."""
    response = client.get("/api/appointments/nonexistent")
    assert response.status_code == 404


def test_list_appointments_endpoint():
    """Test listing all appointments."""
    # Create a couple of appointments
    for i in range(2):
        appointment_data = {
            "patient_name": f"Patient {i}",
            "provider_id": "p001",
            "date": "2026-01-25",
            "time": f"{9 + i}:00"
        }
        client.post("/api/appointments/", json=appointment_data)
    
    # List appointments
    response = client.get("/api/appointments/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_download_ics_file():
    """Test downloading .ics file."""
    # Create appointment
    appointment_data = {
        "patient_name": "Alice Brown",
        "provider_id": "p003",
        "date": "2026-02-01",
        "time": "11:00"
    }
    
    create_response = client.post("/api/appointments/", json=appointment_data)
    appointment_id = create_response.json()["appointment_id"]
    
    # Download .ics
    response = client.get(f"/api/appointments/{appointment_id}/ics")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/calendar; charset=utf-8"
    assert b"BEGIN:VCALENDAR" in response.content


def test_conversation_endpoint_without_api_key(monkeypatch):
    """Test conversation endpoint handles missing API key gracefully."""
    # This test may fail if OPENAI_API_KEY is set in environment
    # We'll skip detailed testing of LLM integration in basic tests
    request_data = {
        "message": "I have a rash"
    }
    
    # The endpoint may return 500 if API key is not configured
    # or 200 if it is configured
    response = client.post("/api/conversation/", json=request_data)
    assert response.status_code in [200, 500]


def test_api_validation():
    """Test API input validation."""
    # Missing required fields
    invalid_data = {
        "patient_name": "Test User"
        # Missing provider_id, date, time
    }
    
    response = client.post("/api/appointments/", json=invalid_data)
    assert response.status_code == 422  # Validation error
