"""
Mock schedule database.
"""
from datetime import datetime, timedelta
from typing import List, Dict
from backend.models.schemas import Schedule
from backend.models.constants import STANDARD_TIME_SLOTS
import random


def generate_mock_schedule(provider_id: str, days_ahead: int = 14) -> List[Schedule]:
    """
    Generate mock schedule data for a provider.
    
    Args:
        provider_id: Provider ID
        days_ahead: Number of days to generate schedules for
        
    Returns:
        List of Schedule objects
    """
    schedules = []
    today = datetime.now().date()
    
    # Use provider_id as seed for consistent but varied schedules per provider
    random.seed(hash(provider_id))
    
    for day_offset in range(1, days_ahead + 1):
        date = today + timedelta(days=day_offset)
        date_str = date.strftime("%Y-%m-%d")
        
        # Skip weekends for simplicity
        if date.weekday() >= 5:
            continue
        
        # Randomly remove some slots to simulate bookings (but keep most slots available)
        available_slots = STANDARD_TIME_SLOTS.copy()
        num_booked = random.randint(2, 4)  # Book fewer slots
        for _ in range(num_booked):
            if available_slots:
                available_slots.pop(random.randint(0, len(available_slots) - 1))
        
        schedules.append(Schedule(
            provider_id=provider_id,
            date=date_str,
            available_slots=available_slots
        ))
    
    # Reset random seed
    random.seed()
    
    return schedules


# Cache for generated schedules
_SCHEDULE_CACHE: Dict[str, List[Schedule]] = {}


def get_provider_schedule(provider_id: str, days_ahead: int = 14) -> List[Schedule]:
    """
    Get schedule for a provider.
    
    Args:
        provider_id: Provider ID
        days_ahead: Number of days to look ahead
        
    Returns:
        List of Schedule objects
    """
    if provider_id not in _SCHEDULE_CACHE:
        _SCHEDULE_CACHE[provider_id] = generate_mock_schedule(provider_id, days_ahead)
    return _SCHEDULE_CACHE[provider_id]


def get_available_slots(provider_id: str, date: str) -> List[str]:
    """
    Get available time slots for a provider on a specific date.
    
    Args:
        provider_id: Provider ID
        date: Date in YYYY-MM-DD format
        
    Returns:
        List of available time slots
    """
    schedules = get_provider_schedule(provider_id)
    for schedule in schedules:
        if schedule.date == date:
            return schedule.available_slots
    return []


def book_slot(provider_id: str, date: str, time: str) -> bool:
    """
    Book a time slot (remove it from available slots).
    
    Args:
        provider_id: Provider ID
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format
        
    Returns:
        True if booking successful, False otherwise
    """
    if provider_id not in _SCHEDULE_CACHE:
        _SCHEDULE_CACHE[provider_id] = generate_mock_schedule(provider_id)
    
    schedules = _SCHEDULE_CACHE[provider_id]
    for schedule in schedules:
        if schedule.date == date and time in schedule.available_slots:
            schedule.available_slots.remove(time)
            return True
    return False


def clear_schedule_cache():
    """Clear the schedule cache (useful for testing)."""
    _SCHEDULE_CACHE.clear()
