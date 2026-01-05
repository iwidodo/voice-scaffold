# CSV Database Quick Start Guide

## Overview

The appointment scheduler now uses a **CSV-based database** for providers and schedules. This provides:

- ✅ Easy demo setup
- ✅ Simple data modification
- ✅ Fast in-memory queries
- ✅ No database server required
- ✅ Clear data visibility

## File Locations

```
appointment-scheduler/backend/database/
├── providers.csv      # Provider data
├── schedules.csv      # Schedule data
├── providers.py       # Provider database code
├── schedules.py       # Schedule database code
└── README.md         # Detailed documentation
```

## Quick Test

Run the test scripts to verify everything works:

```bash
# Basic functionality test
python backend/database/test_csv_db.py

# Full integration test
python backend/database/test_integration.py
```

## Modifying Data

### Add a New Provider

1. Open `backend/database/providers.csv`
2. Add a new row:
   ```csv
   p011,Dr. New Doctor,Dermatologist,10,4.7,"123 New Address"
   ```
3. Restart the application (or reload in code)

### Add Provider Schedules

1. Open `backend/database/schedules.csv`
2. Add schedule rows for the provider:
   ```csv
   p011,2026-01-06,"09:00,09:30,10:00,11:00",1
   p011,2026-01-07,"09:00,09:30,10:00,11:00",1
   ```
3. Restart the application (or reload in code)

### Modify Existing Data

Simply edit the CSV files directly. Changes take effect on restart or reload.

## How It Works

### On Startup
1. CSV files are loaded into memory
2. Data is parsed into Pydantic models
3. In-memory dictionaries/lists created for fast queries

### During Runtime
- All queries use in-memory data (very fast)
- Bookings modify in-memory data
- Optionally persist changes back to CSV

### Data Flow
```
CSV Files → Load on Startup → In-Memory Database → Fast Queries
                ↓
          Pydantic Models
                ↓
          Type-Safe APIs
```

## API Examples

### Get Providers
```python
from backend.database import get_all_providers, get_provider_by_id

# Get all providers
providers = get_all_providers()

# Get specific provider
provider = get_provider_by_id("p001")
```

### Get Schedules
```python
from backend.database import get_provider_schedule, get_available_slots

# Get provider schedule
schedule = get_provider_schedule("p001")

# Get slots for specific date
slots = get_available_slots("p001", "2026-01-06")
```

### Book Appointment
```python
from backend.database import book_slot, save_schedules_to_csv

# Book a slot
book_slot("p001", "2026-01-06", "09:00")

# Optionally save to CSV
save_schedules_to_csv()
```

### Reload Data
```python
from backend.database import clear_schedule_cache, initialize_providers_db

# Reload schedules
clear_schedule_cache()

# Reload providers
initialize_providers_db()
```

## CSV Format Reference

### providers.csv
```csv
id,name,specialty,experience_years,rating,location
p001,Dr. Sarah Johnson,Dermatologist,15,4.8,"123 Medical Plaza, Suite 200"
```

### schedules.csv
```csv
provider_id,date,time_slots,is_available
p001,2026-01-06,"09:00,09:30,10:00,10:30,11:00",1
```

## Specialties

Valid specialty values (must match exactly):
- `General Practitioner`
- `Dermatologist`
- `Cardiologist`
- `Neurologist`
- `Orthopedist`
- `Pediatrician`
- `Psychiatrist`
- `Ophthalmologist`
- `ENT Specialist`

## Standard Time Slots

Default time slots (can be customized per provider):
- Morning: `09:00, 09:30, 10:00, 10:30, 11:00, 11:30`
- Afternoon: `13:00, 13:30, 14:00, 14:30, 15:00, 15:30, 16:00`

## Benefits

### For Demo
- Quick to set up and explain
- Easy to show how data flows
- No complex database setup
- Clear data for presentations

### For Development
- Fast iteration on test data
- No database migrations
- Simple version control
- Easy to debug

### For Testing
- Predictable test data
- Easy to reset state
- Fast test execution
- No test database needed

## Migration Path

When ready to scale:

1. **Keep the API** - All functions remain the same
2. **Swap the backend** - Replace CSV loading with DB queries
3. **No code changes needed** - Just change implementation

Potential targets:
- SQLite (simple file-based DB)
- PostgreSQL (production-grade)
- MongoDB (flexible schema)

## Troubleshooting

### Data not loading?
- Check CSV file exists in correct location
- Verify CSV format (commas, quotes, headers)
- Check logs for parsing errors

### Changes not appearing?
- Restart the application
- Or call reload functions in code

### Booking not persisting?
- Call `save_schedules_to_csv()` after booking
- Or accept that bookings are in-memory only

## Full Documentation

See `backend/database/README.md` for complete documentation.
