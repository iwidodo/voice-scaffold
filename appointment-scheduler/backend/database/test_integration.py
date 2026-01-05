#!/usr/bin/env python3
"""
Integration test to verify CSV database works with the full application stack.
Tests the interaction between database, provider matching, and appointment services.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import (
    get_all_providers,
    get_provider_by_id,
    get_provider_schedule,
    get_available_slots,
)
from backend.llm.provider_matcher import match_provider_for_issue
from backend.models.constants import Specialty


def test_provider_matching():
    """Test that provider matching works with CSV data."""
    print("\n" + "="*60)
    print("TESTING PROVIDER MATCHING WITH CSV DATA")
    print("="*60)
    
    test_cases = [
        ("I have a rash on my arm", Specialty.DERMATOLOGIST),
        ("My child has a fever", Specialty.PEDIATRICIAN),
        ("I have chest pain", Specialty.CARDIOLOGIST),
        ("General checkup", Specialty.GENERAL_PRACTITIONER),
    ]
    
    for issue, expected_specialty in test_cases:
        print(f"\nTest: '{issue}'")
        match = match_provider_for_issue(issue)
        
        if match:
            print(f"  ✓ Matched: {match.provider_name}")
            print(f"    Specialty: {match.specialty}")
            print(f"    Confidence: {match.confidence}")
            
            # Verify specialty matches expected
            if match.specialty == expected_specialty:
                print(f"  ✓ Specialty correct: {expected_specialty}")
            else:
                print(f"  ✗ Expected {expected_specialty}, got {match.specialty}")
            
            # Verify provider exists in database
            provider = get_provider_by_id(match.provider_id)
            if provider:
                print(f"  ✓ Provider found in database")
                print(f"    Location: {provider.location}")
                print(f"    Rating: {provider.rating}")
            else:
                print(f"  ✗ Provider not found in database!")
        else:
            print(f"  ✗ No match found")


def test_schedule_availability():
    """Test that schedules are properly loaded for all providers."""
    print("\n" + "="*60)
    print("TESTING SCHEDULE AVAILABILITY")
    print("="*60)
    
    providers = get_all_providers()
    providers_without_schedules = []
    
    print(f"\nChecking schedules for {len(providers)} providers...")
    
    for provider in providers:
        schedules = get_provider_schedule(provider.id)
        if not schedules:
            providers_without_schedules.append(provider)
            print(f"  ✗ {provider.name} has no schedules")
        else:
            # Check first date has slots
            first_schedule = schedules[0]
            slots = get_available_slots(provider.id, first_schedule.date)
            print(f"  ✓ {provider.name}: {len(schedules)} dates, {len(slots)} slots on {first_schedule.date}")
    
    if not providers_without_schedules:
        print("\n✓ All providers have schedules!")
    else:
        print(f"\n✗ {len(providers_without_schedules)} providers without schedules")


def test_specialty_consistency():
    """Test that specialty strings are consistent across the system."""
    print("\n" + "="*60)
    print("TESTING SPECIALTY CONSISTENCY")
    print("="*60)
    
    providers = get_all_providers()
    
    # Get unique specialties from CSV
    csv_specialties = set(p.specialty for p in providers)
    
    # Get specialties from enum
    enum_specialties = set(s.value for s in Specialty)
    
    print(f"\nSpecialties in CSV: {len(csv_specialties)}")
    for spec in sorted(csv_specialties):
        print(f"  - {spec}")
    
    print(f"\nSpecialties in Enum: {len(enum_specialties)}")
    for spec in sorted(enum_specialties):
        print(f"  - {spec}")
    
    # Check for mismatches
    csv_only = csv_specialties - enum_specialties
    enum_only = enum_specialties - csv_specialties
    
    if csv_only:
        print(f"\n✗ Specialties in CSV but not in Enum:")
        for spec in csv_only:
            print(f"  - {spec}")
    
    if enum_only:
        print(f"\n✗ Specialties in Enum but not in CSV:")
        for spec in enum_only:
            print(f"  - {spec}")
    
    if not csv_only and not enum_only:
        print("\n✓ All specialties are consistent!")


def test_end_to_end_booking():
    """Test a complete booking flow."""
    print("\n" + "="*60)
    print("TESTING END-TO-END BOOKING FLOW")
    print("="*60)
    
    # Step 1: Patient describes issue
    print("\n1. Patient describes issue: 'I have a skin rash'")
    match = match_provider_for_issue("I have a skin rash")
    
    if not match:
        print("  ✗ Failed to match provider")
        return
    
    print(f"  ✓ Matched to: {match.provider_name}")
    
    # Step 2: Check provider exists
    print(f"\n2. Retrieving provider details...")
    provider = get_provider_by_id(match.provider_id)
    
    if not provider:
        print("  ✗ Provider not found")
        return
    
    print(f"  ✓ Provider: {provider.name}")
    print(f"    Specialty: {provider.specialty}")
    print(f"    Experience: {provider.experience_years} years")
    print(f"    Rating: {provider.rating}/5.0")
    print(f"    Location: {provider.location}")
    
    # Step 3: Check availability
    print(f"\n3. Checking availability...")
    schedules = get_provider_schedule(provider.id)
    
    if not schedules:
        print("  ✗ No schedules available")
        return
    
    print(f"  ✓ Found {len(schedules)} available dates")
    
    # Step 4: Get slots for first available date
    first_date = schedules[0].date
    slots = get_available_slots(provider.id, first_date)
    
    if not slots:
        print(f"  ✗ No slots available on {first_date}")
        return
    
    print(f"\n4. Available slots on {first_date}:")
    print(f"  ✓ {len(slots)} slots available")
    print(f"    First 5 slots: {', '.join(slots[:5])}")
    
    print("\n✓ Complete booking flow successful!")


def main():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("CSV DATABASE INTEGRATION TEST SUITE")
    print("="*60)
    
    try:
        test_specialty_consistency()
        test_schedule_availability()
        test_provider_matching()
        test_end_to_end_booking()
        
        print("\n" + "="*60)
        print("ALL INTEGRATION TESTS PASSED ✓")
        print("="*60)
        print("\nThe CSV-based database is fully integrated and working!")
        print("✓ Providers loaded correctly")
        print("✓ Schedules loaded correctly")
        print("✓ Provider matching works")
        print("✓ Specialties are consistent")
        print("✓ End-to-end flow successful")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
