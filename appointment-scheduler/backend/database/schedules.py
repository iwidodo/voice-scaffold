"""
CSV-based schedule database.
Loads schedule data from CSV file on startup and maintains it in-memory for fast queries.
"""
import logging
import csv
from pathlib import Path
from typing import List, Dict
from backend.models.schemas import Schedule

logger = logging.getLogger(__name__)

# In-memory schedule database (loaded from CSV)
# Structure: {provider_id: [Schedule, Schedule, ...]}
SCHEDULES_DB: Dict[str, List[Schedule]] = {}

# Path to the CSV file
CSV_FILE = Path(__file__).parent / "schedules.csv"


def load_schedules_from_csv() -> Dict[str, List[Schedule]]:
    """
    Load schedules from CSV file.
    
    Returns:
        Dictionary mapping provider_id to list of Schedule objects
    """
    schedules_dict: Dict[str, List[Schedule]] = {}
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse time slots from comma-separated string
                time_slots = [slot.strip() for slot in row['time_slots'].split(',')]
                
                schedule = Schedule(
                    provider_id=row['provider_id'],
                    date=row['date'],
                    available_slots=time_slots
                )
                
                # Group schedules by provider_id
                if schedule.provider_id not in schedules_dict:
                    schedules_dict[schedule.provider_id] = []
                schedules_dict[schedule.provider_id].append(schedule)
        
        total_schedules = sum(len(schedules) for schedules in schedules_dict.values())
        logger.info(f"[schedules.py.load_schedules_from_csv] Loaded {total_schedules} schedule entries for {len(schedules_dict)} providers")
    except FileNotFoundError:
        logger.error(f"[schedules.py.load_schedules_from_csv] CSV file not found: {CSV_FILE}")
    except Exception as e:
        logger.error(f"[schedules.py.load_schedules_from_csv] Error loading CSV: {e}")
    
    return schedules_dict


def initialize_database():
    """Initialize the schedule database by loading from CSV."""
    global SCHEDULES_DB
    SCHEDULES_DB = load_schedules_from_csv()
    logger.info(f"[schedules.py.initialize_database] Database initialized with schedules for {len(SCHEDULES_DB)} providers")


# Initialize on module load
initialize_database()


def get_provider_schedule(provider_id: str, days_ahead: int = 14) -> List[Schedule]:
    """
    Get schedule for a provider.
    
    Args:
        provider_id: Provider ID
        days_ahead: Number of days to look ahead (not used with CSV data, but kept for API compatibility)
        
    Returns:
        List of Schedule objects
    """
    logger.debug(f"[schedules.py.get_provider_schedule] Getting schedule for provider: {provider_id}")
    
    if provider_id in SCHEDULES_DB:
        schedules = SCHEDULES_DB[provider_id]
        logger.debug(f"[schedules.py.get_provider_schedule] Found {len(schedules)} schedule entries")
        return schedules
    
    logger.warning(f"[schedules.py.get_provider_schedule] No schedules found for provider: {provider_id}")
    return []


def get_available_slots(provider_id: str, date: str) -> List[str]:
    """
    Get available time slots for a provider on a specific date.
    
    Args:
        provider_id: Provider ID
        date: Date in YYYY-MM-DD format
        
    Returns:
        List of available time slots
    """
    logger.debug(f"[schedules.py.get_available_slots] Getting available slots for provider: {provider_id}, date: {date}")
    
    schedules = get_provider_schedule(provider_id)
    for schedule in schedules:
        if schedule.date == date:
            logger.debug(f"[schedules.py.get_available_slots] Found {len(schedule.available_slots)} slots for {date}")
            return schedule.available_slots
    
    logger.debug(f"[schedules.py.get_available_slots] No slots found for provider: {provider_id}, date: {date}")
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
    logger.info(f"[schedules.py.book_slot] Booking slot for provider: {provider_id}, date: {date}, time: {time}")
    
    if provider_id not in SCHEDULES_DB:
        logger.warning(f"[schedules.py.book_slot] Provider not found in database: {provider_id}")
        return False
    
    schedules = SCHEDULES_DB[provider_id]
    for schedule in schedules:
        if schedule.date == date and time in schedule.available_slots:
            schedule.available_slots.remove(time)
            logger.info(f"[schedules.py.book_slot] Slot booked successfully: {date} at {time}")
            
            # Automatically save to CSV to persist the booking
            save_result = save_schedules_to_csv()
            if save_result:
                logger.info(f"[schedules.py.book_slot] Booking persisted to CSV")
            else:
                logger.warning(f"[schedules.py.book_slot] Failed to persist booking to CSV")
            
            return True
    
    logger.warning(f"[schedules.py.book_slot] Failed to book slot - not available: {date} at {time}")
    return False


def clear_schedule_cache():
    """
    Clear the schedule cache and reload from CSV (useful for testing).
    """
    logger.info(f"[schedules.py.clear_schedule_cache] Reloading schedules from CSV")
    initialize_database()


def save_schedules_to_csv():
    """
    Save the current in-memory schedules back to CSV file.
    This allows for persistence of booked appointments.
    """
    try:
        with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['provider_id', 'date', 'time_slots', 'is_available']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for provider_id, schedules in sorted(SCHEDULES_DB.items()):
                for schedule in sorted(schedules, key=lambda s: s.date):
                    writer.writerow({
                        'provider_id': schedule.provider_id,
                        'date': schedule.date,
                        'time_slots': ','.join(schedule.available_slots),
                        'is_available': '1'
                    })
        
        logger.info(f"[schedules.py.save_schedules_to_csv] Saved schedules to CSV")
        return True
    except Exception as e:
        logger.error(f"[schedules.py.save_schedules_to_csv] Error saving CSV: {e}")
        return False
