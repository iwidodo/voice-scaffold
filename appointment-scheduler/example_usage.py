#!/usr/bin/env python
"""
Example usage of the appointment scheduling system.

This script demonstrates how to use both the conversation API 
and the direct appointment API.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database.schedules import get_provider_schedule
from backend.llm.provider_matcher import match_provider_for_issue


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print('=' * 60)


def example_provider_matching():
    """Demonstrate provider matching."""
    print_section("Example 1: Provider Matching")
    
    health_issues = [
        "I have a rash on my skin",
        "I'm experiencing severe headaches",
        "I have chest pain and palpitations",
        "My back hurts when I move",
    ]
    
    for issue in health_issues:
        print(f"\nPatient says: '{issue}'")
        match = match_provider_for_issue(issue)
        if match:
            print(f"  → Matched Provider: {match.provider_name}")
            print(f"  → Specialty: {match.specialty}")
            print(f"  → Confidence: {match.confidence:.1%}")


def example_direct_appointment():
    """Demonstrate direct appointment creation."""
    print_section("Example 2: Direct Appointment Creation")
    
    client = TestClient(app)
    
    # Get available slots
    schedules = get_provider_schedule('p001')
    if not schedules or not schedules[0].available_slots:
        print("No available slots found")
        return
    
    date = schedules[0].date
    time = schedules[0].available_slots[0]
    
    print(f"\nCreating appointment for {date} at {time}")
    
    appointment_data = {
        "patient_name": "John Doe",
        "provider_id": "p001",
        "date": date,
        "time": time,
        "reason": "Skin consultation"
    }
    
    response = client.post("/api/appointments/", json=appointment_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Appointment Created Successfully!")
        print(f"  Appointment ID: {data['appointment_id']}")
        print(f"  Provider: {data['provider_name']}")
        print(f"  Location: {data['location']}")
        print(f"  Date: {data['date']} at {data['time']}")
        print(f"  .ics file: {'Available' if data.get('ics_file') else 'Not available'}")
        
        # Download .ics file
        ics_response = client.get(f"/api/appointments/{data['appointment_id']}/ics")
        if ics_response.status_code == 200:
            print(f"  .ics file size: {len(ics_response.content)} bytes")
    else:
        print(f"✗ Failed to create appointment: {response.json()}")


def example_conversation_flow():
    """Demonstrate conversation-based booking (mock without real OpenAI API)."""
    print_section("Example 3: Conversation Flow (Simulated)")
    
    print("\nThis would be a typical conversation flow:")
    print("\nUser: 'I have a rash, who should I see?'")
    print("Assistant: 'I recommend Dr. Sarah Johnson, a dermatologist...'")
    print("\nUser: 'When can I see them?'")
    print("Assistant: 'Here are available times...'")
    print("\nUser: 'Book me for Monday at 10:00'")
    print("Assistant: 'Appointment confirmed! I've created an .ics file...'")
    print("\n(Note: Real conversation requires OPENAI_API_KEY)")


def example_availability_check():
    """Demonstrate checking provider availability."""
    print_section("Example 4: Checking Provider Availability")
    
    from backend.services.schedule_service import (
        get_availability_summary,
        format_availability_message
    )
    
    print("\nChecking availability for Dr. Sarah Johnson (p001)")
    
    availability = get_availability_summary("p001", num_days=5)
    if availability:
        formatted = format_availability_message(availability)
        print("\nAvailable appointments:")
        print(formatted)
    else:
        print("No available slots found")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Appointment Scheduling System - Examples")
    print("=" * 60)
    
    try:
        example_provider_matching()
        example_direct_appointment()
        example_availability_check()
        example_conversation_flow()
        
        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)
        print("\nTo run the API server:")
        print("  cd appointment-scheduler")
        print("  ./run_local.sh")
        print("\nAPI Documentation will be at:")
        print("  http://localhost:8000/docs")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
