"""
Schedule service for handling availability queries.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from backend.database.schedules import get_provider_schedule, get_available_slots
from backend.models.schemas import Schedule


def get_next_available_dates(provider_id: str, num_dates: int = 5) -> List[str]:
    """
    Get the next N available dates for a provider.
    
    Args:
        provider_id: Provider ID
        num_dates: Number of dates to return
        
    Returns:
        List of dates in YYYY-MM-DD format
    """
    schedules = get_provider_schedule(provider_id)
    available_dates = []
    
    for schedule in schedules:
        if schedule.available_slots:
            available_dates.append(schedule.date)
            if len(available_dates) >= num_dates:
                break
    
    return available_dates


def get_availability_summary(provider_id: str, num_days: int = 7) -> Dict[str, List[str]]:
    """
    Get availability summary for a provider.
    
    Args:
        provider_id: Provider ID
        num_days: Number of days to check
        
    Returns:
        Dictionary mapping dates to available time slots
    """
    schedules = get_provider_schedule(provider_id, days_ahead=num_days)
    summary = {}
    
    for schedule in schedules:
        if schedule.available_slots:
            summary[schedule.date] = schedule.available_slots
    
    return summary


def find_common_availability(
    provider_id: str,
    user_preferred_dates: List[str],
    user_preferred_times: Optional[List[str]] = None
) -> Dict[str, List[str]]:
    """
    Find common availability between provider and user preferences.
    
    Args:
        provider_id: Provider ID
        user_preferred_dates: List of dates user prefers (YYYY-MM-DD format)
        user_preferred_times: Optional list of times user prefers (HH:MM format)
        
    Returns:
        Dictionary mapping dates to available time slots that match preferences
    """
    result = {}
    
    for date in user_preferred_dates:
        available_slots = get_available_slots(provider_id, date)
        
        if user_preferred_times:
            # Filter by user's preferred times
            matching_slots = [slot for slot in available_slots if slot in user_preferred_times]
            if matching_slots:
                result[date] = matching_slots
        else:
            if available_slots:
                result[date] = available_slots
    
    return result


def get_earliest_available_slot(provider_id: str) -> Optional[tuple]:
    """
    Get the earliest available slot for a provider.
    
    Args:
        provider_id: Provider ID
        
    Returns:
        Tuple of (date, time) or None if no slots available
    """
    schedules = get_provider_schedule(provider_id)
    
    for schedule in schedules:
        if schedule.available_slots:
            # Slots are already in chronological order
            return (schedule.date, schedule.available_slots[0])
    
    return None


def format_availability_message(availability: Dict[str, List[str]]) -> str:
    """
    Format availability dictionary into a human-readable message.
    
    Args:
        availability: Dictionary mapping dates to time slots
        
    Returns:
        Formatted string
    """
    if not availability:
        return "No available slots found."
    
    messages = []
    for date, slots in sorted(availability.items()):
        # Parse and format date nicely
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%A, %B %d, %Y")
        
        # Group morning and afternoon slots
        morning_slots = [s for s in slots if int(s.split(":")[0]) < 12]
        afternoon_slots = [s for s in slots if int(s.split(":")[0]) >= 12]
        
        slot_parts = []
        if morning_slots:
            slot_parts.append(f"Morning: {', '.join(morning_slots)}")
        if afternoon_slots:
            slot_parts.append(f"Afternoon: {', '.join(afternoon_slots)}")
        
        messages.append(f"{formatted_date}: {' | '.join(slot_parts)}")
    
    return "\n".join(messages)
