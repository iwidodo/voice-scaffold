"""
Tests for schedule service.
"""
import pytest
from backend.services.schedule_service import (
    get_next_available_dates,
    get_availability_summary,
    find_common_availability,
    get_earliest_available_slot,
    format_availability_message
)
from backend.database.schedules import clear_schedule_cache


@pytest.fixture(autouse=True)
def reset_schedules():
    """Reset schedule cache before each test."""
    clear_schedule_cache()
    yield
    clear_schedule_cache()


def test_get_next_available_dates():
    """Test getting next available dates."""
    dates = get_next_available_dates("p001", num_dates=3)
    assert len(dates) <= 3
    assert all(isinstance(d, str) for d in dates)
    # Dates should be in YYYY-MM-DD format
    for date in dates:
        assert len(date) == 10
        assert date.count("-") == 2


def test_get_availability_summary():
    """Test getting availability summary."""
    summary = get_availability_summary("p001", num_days=7)
    assert isinstance(summary, dict)
    # Should have dates as keys and time slots as values
    for date, slots in summary.items():
        assert isinstance(date, str)
        assert isinstance(slots, list)
        assert all(isinstance(s, str) for s in slots)


def test_find_common_availability_with_dates():
    """Test finding common availability with preferred dates."""
    # Get some available dates first
    available_dates = get_next_available_dates("p001", num_dates=3)
    
    if available_dates:
        # Use first two dates as preferences
        preferred = available_dates[:2]
        common = find_common_availability("p001", preferred)
        
        assert isinstance(common, dict)
        # Should only include dates that were in preferences
        for date in common.keys():
            assert date in preferred


def test_find_common_availability_with_times():
    """Test finding common availability with preferred times."""
    available_dates = get_next_available_dates("p001", num_dates=2)
    
    if available_dates:
        preferred_times = ["09:00", "10:00"]
        common = find_common_availability(
            "p001",
            available_dates,
            user_preferred_times=preferred_times
        )
        
        # All returned slots should be in preferred times
        for date, slots in common.items():
            for slot in slots:
                assert slot in preferred_times


def test_get_earliest_available_slot():
    """Test getting earliest available slot."""
    slot = get_earliest_available_slot("p001")
    
    if slot:
        date, time = slot
        assert isinstance(date, str)
        assert isinstance(time, str)
        assert len(date) == 10  # YYYY-MM-DD
        assert ":" in time  # HH:MM


def test_format_availability_message():
    """Test formatting availability message."""
    availability = {
        "2026-01-15": ["09:00", "10:00", "14:00", "15:00"],
        "2026-01-16": ["11:00", "13:00"]
    }
    
    message = format_availability_message(availability)
    assert isinstance(message, str)
    assert "2026" in message or "January" in message  # Should contain date info
    assert "Morning" in message or "Afternoon" in message  # Should categorize times


def test_format_empty_availability():
    """Test formatting empty availability."""
    message = format_availability_message({})
    assert "No available slots" in message


def test_availability_returns_valid_time_slots():
    """Test that availability returns valid time slots."""
    summary = get_availability_summary("p001", num_days=5)
    
    for date, slots in summary.items():
        for slot in slots:
            # Should be in HH:MM format
            parts = slot.split(":")
            assert len(parts) == 2
            hour, minute = parts
            assert hour.isdigit() and minute.isdigit()
            assert 0 <= int(hour) <= 23
            assert 0 <= int(minute) <= 59
