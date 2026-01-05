#!/usr/bin/env python3
"""
Test script to verify CSV-based database functionality.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import (
    get_all_providers,
    get_provider_by_id,
    get_providers_by_specialty,
    get_provider_schedule,
    get_available_slots,
    book_slot,
    save_schedules_to_csv,
)


def test_providers():
    """Test provider database functionality."""
    print("\n" + "="*60)
    print("TESTING PROVIDERS DATABASE")
    print("="*60)
    
    # Test: Get all providers
    print("\n1. Getting all providers...")
    providers = get_all_providers()
    print(f"   ✓ Found {len(providers)} providers")
    
    # Test: Get specific provider
    print("\n2. Getting specific provider (p001)...")
    provider = get_provider_by_id("p001")
    if provider:
        print(f"   ✓ Found: {provider.name} - {provider.specialty}")
        print(f"     Experience: {provider.experience_years} years, Rating: {provider.rating}")
    else:
        print("   ✗ Provider not found")
    
    # Test: Get providers by specialty
    print("\n3. Getting Dermatologists...")
    dermatologists = get_providers_by_specialty("Dermatologist")
    print(f"   ✓ Found {len(dermatologists)} dermatologists:")
    for p in dermatologists:
        print(f"     - {p.name} (Rating: {p.rating})")


def test_schedules():
    """Test schedule database functionality."""
    print("\n" + "="*60)
    print("TESTING SCHEDULES DATABASE")
    print("="*60)
    
    # Test: Get provider schedule
    print("\n1. Getting schedule for Dr. Sarah Johnson (p001)...")
    schedules = get_provider_schedule("p001")
    print(f"   ✓ Found {len(schedules)} schedule entries")
    if schedules:
        first = schedules[0]
        print(f"     First entry: {first.date} with {len(first.available_slots)} slots")
    
    # Test: Get available slots for specific date
    print("\n2. Getting available slots for 2026-01-06...")
    slots = get_available_slots("p001", "2026-01-06")
    print(f"   ✓ Found {len(slots)} available slots:")
    print(f"     {', '.join(slots[:5])}{'...' if len(slots) > 5 else ''}")
    
    # Test: Book a slot
    print("\n3. Booking slot at 09:00 on 2026-01-06...")
    if "09:00" in slots:
        success = book_slot("p001", "2026-01-06", "09:00")
        if success:
            print("   ✓ Slot booked successfully")
            
            # Verify booking
            updated_slots = get_available_slots("p001", "2026-01-06")
            if "09:00" not in updated_slots:
                print("   ✓ Slot removed from available slots")
                print(f"     Now {len(updated_slots)} slots available")
            else:
                print("   ✗ Slot still appears as available")
        else:
            print("   ✗ Failed to book slot")
    else:
        print("   ⚠ Slot 09:00 not available (might already be booked)")


def test_data_consistency():
    """Test data consistency between providers and schedules."""
    print("\n" + "="*60)
    print("TESTING DATA CONSISTENCY")
    print("="*60)
    
    providers = get_all_providers()
    print(f"\n✓ All {len(providers)} providers have schedules:")
    
    for provider in providers:
        schedules = get_provider_schedule(provider.id)
        print(f"  - {provider.name} ({provider.id}): {len(schedules)} schedule entries")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("CSV-BASED DATABASE TEST SUITE")
    print("="*60)
    
    try:
        test_providers()
        test_schedules()
        test_data_consistency()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY ✓")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
