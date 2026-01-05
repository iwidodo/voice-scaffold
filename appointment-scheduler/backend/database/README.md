# CSV-Based Database

This directory contains a simple CSV-based database system for managing providers and their schedules. The data is loaded from CSV files on startup and maintained in-memory for fast querying.

## Structure

### Files

- **`providers.csv`** - Healthcare provider information
- **`schedules.csv`** - Provider availability schedules
- **`providers.py`** - Provider database module
- **`schedules.py`** - Schedule database module

## CSV Format

### providers.csv

Contains information about healthcare providers:

```csv
id,name,specialty,experience_years,rating,location
p001,Dr. Sarah Johnson,Dermatologist,15,4.8,"123 Medical Plaza, Suite 200"
```

**Columns:**
- `id` - Unique provider identifier (e.g., p001, p002)
- `name` - Provider's full name
- `specialty` - Medical specialty (e.g., Dermatologist, Cardiologist)
- `experience_years` - Years of experience (integer)
- `rating` - Provider rating (float, 0.0-5.0)
- `location` - Office address

### schedules.csv

Contains provider availability information:

```csv
provider_id,date,time_slots,is_available
p001,2026-01-06,"09:00,09:30,10:00,10:30,11:00,11:30,13:00,13:30",1
```

**Columns:**
- `provider_id` - Reference to provider ID from providers.csv
- `date` - Date in YYYY-MM-DD format
- `time_slots` - Comma-separated list of available time slots (HH:MM format)
- `is_available` - Flag indicating if provider is available (1=yes, 0=no)

## Usage

### Loading Data

Data is automatically loaded when the modules are imported:

```python
from backend.database import providers, schedules

# Data is already loaded and ready to use
```

### Querying Providers

```python
from backend.database import get_all_providers, get_provider_by_id

# Get all providers
all_providers = get_all_providers()

# Get specific provider
provider = get_provider_by_id("p001")

# Get providers by specialty
from backend.database import get_providers_by_specialty
dermatologists = get_providers_by_specialty("Dermatologist")
```

### Querying Schedules

```python
from backend.database import get_provider_schedule, get_available_slots

# Get all schedules for a provider
schedules = get_provider_schedule("p001")

# Get available slots for a specific date
slots = get_available_slots("p001", "2026-01-06")
```

### Booking Appointments

```python
from backend.database import book_slot, save_schedules_to_csv

# Book a time slot
success = book_slot("p001", "2026-01-06", "09:00")

# Optionally save changes back to CSV
save_schedules_to_csv()
```

### Reloading Data

```python
from backend.database import clear_schedule_cache, initialize_providers_db

# Reload schedules from CSV
clear_schedule_cache()

# Reload providers from CSV
initialize_providers_db()
```

## Benefits

✅ **Quick to Demo** - Simple CSV files are easy to understand and modify  
✅ **Easy to Modify** - Edit CSV files directly to change test data  
✅ **Shows LLM Logic** - Clean separation between data and business logic  
✅ **No Operational Overhead** - No database server or ORM required  
✅ **Fast Queries** - In-memory data structure for instant lookups  
✅ **Persistent Changes** - Optional CSV persistence for booked appointments  

## Adding New Data

### Adding a Provider

1. Open `providers.csv`
2. Add a new row with the next available ID (e.g., p011)
3. Fill in all required fields
4. Restart the application or call `initialize_providers_db()`

### Adding Schedules

1. Open `schedules.csv`
2. Add rows for each date the provider is available
3. List available time slots as comma-separated values
4. Restart the application or call `clear_schedule_cache()`

## Time Slots

Standard time slots are in 30-minute increments:
- Morning: 09:00, 09:30, 10:00, 10:30, 11:00, 11:30
- Afternoon: 13:00, 13:30, 14:00, 14:30, 15:00, 15:30, 16:00

You can customize time slots per provider by editing the `time_slots` column in `schedules.csv`.

## Testing

The CSV-based approach is ideal for testing:

```python
# Reset to original state
clear_schedule_cache()  # Reloads from CSV
initialize_providers_db()  # Reloads from CSV

# Make test bookings without affecting CSV
book_slot("p001", "2026-01-06", "09:00")

# Optionally persist test data
save_schedules_to_csv()
```

## Migration Path

If you need to scale beyond CSV:

1. **SQLite** - Add `sqlite3` database with same schema
2. **PostgreSQL** - Use production-grade RDBMS
3. **NoSQL** - Use MongoDB or similar for flexibility

The function interfaces remain the same, so migration is straightforward.
