"""
Constants and enums for the appointment scheduling system.
"""
from enum import Enum


class ConversationState(str, Enum):
    """States in the conversation flow."""
    INITIAL = "initial"
    ISSUE_IDENTIFIED = "issue_identified"
    PROVIDER_MATCHED = "provider_matched"
    AVAILABILITY_CHECKED = "availability_checked"
    APPOINTMENT_CONFIRMED = "appointment_confirmed"


class Specialty(str, Enum):
    """Medical specialties."""
    GENERAL_PRACTITIONER = "General Practitioner"
    DERMATOLOGIST = "Dermatologist"
    CARDIOLOGIST = "Cardiologist"
    NEUROLOGIST = "Neurologist"
    ORTHOPEDIST = "Orthopedist"
    PEDIATRICIAN = "Pediatrician"
    PSYCHIATRIST = "Psychiatrist"
    OPHTHALMOLOGIST = "Ophthalmologist"
    ENT_SPECIALIST = "ENT Specialist"


# Mapping of health issues to specialties
ISSUE_TO_SPECIALTY = {
    # Skin issues
    "rash": Specialty.DERMATOLOGIST,
    "acne": Specialty.DERMATOLOGIST,
    "eczema": Specialty.DERMATOLOGIST,
    "psoriasis": Specialty.DERMATOLOGIST,
    "skin": Specialty.DERMATOLOGIST,
    "mole": Specialty.DERMATOLOGIST,
    
    # Heart issues
    "chest pain": Specialty.CARDIOLOGIST,
    "heart": Specialty.CARDIOLOGIST,
    "palpitations": Specialty.CARDIOLOGIST,
    "blood pressure": Specialty.CARDIOLOGIST,
    
    # Neurological issues
    "headache": Specialty.NEUROLOGIST,
    "migraine": Specialty.NEUROLOGIST,
    "seizure": Specialty.NEUROLOGIST,
    "dizziness": Specialty.NEUROLOGIST,
    "numbness": Specialty.NEUROLOGIST,
    
    # Bone/joint issues
    "back pain": Specialty.ORTHOPEDIST,
    "back": Specialty.ORTHOPEDIST,
    "joint pain": Specialty.ORTHOPEDIST,
    "joint": Specialty.ORTHOPEDIST,
    "fracture": Specialty.ORTHOPEDIST,
    "arthritis": Specialty.ORTHOPEDIST,
    "sprain": Specialty.ORTHOPEDIST,
    "knee": Specialty.ORTHOPEDIST,
    "shoulder": Specialty.ORTHOPEDIST,
    
    # Children's issues
    "child": Specialty.PEDIATRICIAN,
    "baby": Specialty.PEDIATRICIAN,
    "infant": Specialty.PEDIATRICIAN,
    
    # Mental health
    "depression": Specialty.PSYCHIATRIST,
    "anxiety": Specialty.PSYCHIATRIST,
    "panic": Specialty.PSYCHIATRIST,
    "stress": Specialty.PSYCHIATRIST,
    
    # Eye issues
    "vision": Specialty.OPHTHALMOLOGIST,
    "eye": Specialty.OPHTHALMOLOGIST,
    "blurry": Specialty.OPHTHALMOLOGIST,
    
    # ENT issues
    "ear": Specialty.ENT_SPECIALIST,
    "throat": Specialty.ENT_SPECIALIST,
    "nose": Specialty.ENT_SPECIALIST,
    "sinus": Specialty.ENT_SPECIALIST,
    "hearing": Specialty.ENT_SPECIALIST,
}


# Time slots (in 24-hour format)
STANDARD_TIME_SLOTS = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
    "16:00", "16:30"
]
