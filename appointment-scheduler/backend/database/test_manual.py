#!/usr/bin/env python3
"""
Manual test to verify existing functionality still works with CSV database.
This replicates the key tests without requiring pytest.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.llm.provider_matcher import match_provider_for_issue
from backend.models.constants import Specialty
from backend.database import clear_schedule_cache


def test_provider_matching():
    """Test provider matching scenarios."""
    print("\n" + "="*60)
    print("TESTING PROVIDER MATCHER (CSV Integration)")
    print("="*60)
    
    tests = [
        ("I have a rash on my arm", Specialty.DERMATOLOGIST, "Dermatologist"),
        ("I have severe headaches", Specialty.NEUROLOGIST, "Neurologist"),
        ("I have chest pain", Specialty.CARDIOLOGIST, "Cardiologist"),
        ("My child has a fever", Specialty.PEDIATRICIAN, "Pediatrician"),
        ("General checkup needed", Specialty.GENERAL_PRACTITIONER, "GP"),
        ("I feel depressed", Specialty.PSYCHIATRIST, "Psychiatrist"),
    ]
    
    passed = 0
    failed = 0
    
    for issue, expected_specialty, name in tests:
        result = match_provider_for_issue(issue)
        
        if result is None:
            print(f"✗ {name}: No match found")
            failed += 1
            continue
        
        if result.specialty == expected_specialty:
            print(f"✓ {name}: Matched {result.provider_name} ({result.specialty})")
            passed += 1
        else:
            print(f"✗ {name}: Expected {expected_specialty}, got {result.specialty}")
            failed += 1
        
        if result.confidence < 0.5:
            print(f"  ⚠ Low confidence: {result.confidence}")
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_schedule_functionality():
    """Test schedule operations."""
    print("\n" + "="*60)
    print("TESTING SCHEDULE OPERATIONS (CSV Integration)")
    print("="*60)
    
    from backend.database import (
        get_provider_schedule,
        get_available_slots,
        book_slot,
    )
    
    # Test getting schedule
    print("\n1. Getting schedule for provider p001...")
    schedule = get_provider_schedule("p001")
    
    if not schedule:
        print("✗ Failed to get schedule")
        return False
    
    print(f"✓ Got {len(schedule)} schedule entries")
    
    # Test getting slots
    print("\n2. Getting available slots for 2026-01-06...")
    first_date = schedule[0].date
    slots = get_available_slots("p001", first_date)
    
    if not slots:
        print("✗ No slots available")
        return False
    
    print(f"✓ Found {len(slots)} available slots")
    initial_count = len(slots)
    
    # Test booking
    print(f"\n3. Booking first available slot ({slots[0]})...")
    success = book_slot("p001", first_date, slots[0])
    
    if not success:
        print("✗ Failed to book slot")
        return False
    
    print("✓ Slot booked successfully")
    
    # Verify booking
    print("\n4. Verifying slot was removed...")
    updated_slots = get_available_slots("p001", first_date)
    
    if len(updated_slots) == initial_count - 1:
        print(f"✓ Slot count reduced from {initial_count} to {len(updated_slots)}")
        return True
    else:
        print(f"✗ Expected {initial_count - 1} slots, got {len(updated_slots)}")
        return False


def test_data_reload():
    """Test reloading data from CSV."""
    print("\n" + "="*60)
    print("TESTING DATA RELOAD (CSV Integration)")
    print("="*60)
    
    from backend.database import (
        get_provider_schedule,
        get_available_slots,
        book_slot,
        clear_schedule_cache,
    )
    
    # Book a slot
    print("\n1. Booking a slot...")
    schedule = get_provider_schedule("p002")
    if not schedule:
        print("✗ No schedule found")
        return False
    
    first_date = schedule[0].date
    slots = get_available_slots("p002", first_date)
    if not slots:
        print("✗ No slots available")
        return False
    
    first_slot = slots[0]
    initial_count = len(slots)
    book_slot("p002", first_date, first_slot)
    print(f"✓ Booked {first_slot}")
    
    # Verify booking
    updated_slots = get_available_slots("p002", first_date)
    if len(updated_slots) >= initial_count:
        print("✗ Slot not removed")
        return False
    
    print(f"✓ Slot removed ({initial_count} → {len(updated_slots)})")
    
    # Reload from CSV
    print("\n2. Reloading schedules from CSV...")
    clear_schedule_cache()
    print("✓ Cache cleared and reloaded")
    
    # Verify slot is back
    reloaded_slots = get_available_slots("p002", first_date)
    if len(reloaded_slots) == initial_count:
        print(f"✓ Slot restored ({len(reloaded_slots)} slots)")
        return True
    else:
        print(f"✗ Expected {initial_count} slots, got {len(reloaded_slots)}")
        return False


def main():
    """Run all manual tests."""
    print("\n" + "="*60)
    print("MANUAL TEST SUITE - CSV DATABASE INTEGRATION")
    print("="*60)
    
    results = []
    
    try:
        results.append(("Provider Matching", test_provider_matching()))
        results.append(("Schedule Operations", test_schedule_functionality()))
        results.append(("Data Reload", test_data_reload()))
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        all_passed = True
        for name, passed in results:
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"{name}: {status}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n" + "="*60)
            print("ALL TESTS PASSED ✓")
            print("="*60)
            print("\nThe CSV database is fully functional and integrated!")
            print("✓ Provider matching works correctly")
            print("✓ Schedule operations work correctly")
            print("✓ Data reload from CSV works correctly")
            print("="*60 + "\n")
            return 0
        else:
            print("\n✗ Some tests failed")
            return 1
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
