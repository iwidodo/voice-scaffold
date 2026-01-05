"""
Database package - CSV-based database for providers and schedules.

This module loads data from CSV files on startup and maintains it in-memory for fast queries.
"""

from backend.database import providers, schedules

# Export commonly used functions
from backend.database.providers import (
    get_all_providers,
    get_provider_by_id,
    get_providers_by_specialty,
    get_best_provider_for_specialty,
    initialize_database as initialize_providers_db
)

from backend.database.schedules import (
    get_provider_schedule,
    get_available_slots,
    book_slot,
    clear_schedule_cache,
    save_schedules_to_csv,
    initialize_database as initialize_schedules_db
)

__all__ = [
    # Provider functions
    'get_all_providers',
    'get_provider_by_id',
    'get_providers_by_specialty',
    'get_best_provider_for_specialty',
    'initialize_providers_db',
    
    # Schedule functions
    'get_provider_schedule',
    'get_available_slots',
    'book_slot',
    'clear_schedule_cache',
    'save_schedules_to_csv',
    'initialize_schedules_db',
]
