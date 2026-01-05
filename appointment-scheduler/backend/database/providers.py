"""
Mock provider database.
"""
import logging
from typing import List, Optional
from backend.models.schemas import Provider
from backend.models.constants import Specialty

logger = logging.getLogger(__name__)

# Mock provider data
PROVIDERS_DB = [
    Provider(
        id="p001",
        name="Dr. Sarah Johnson",
        specialty=Specialty.DERMATOLOGIST,
        experience_years=15,
        rating=4.8,
        location="123 Medical Plaza, Suite 200"
    ),
    Provider(
        id="p002",
        name="Dr. Michael Chen",
        specialty=Specialty.DERMATOLOGIST,
        experience_years=8,
        rating=4.6,
        location="456 Healthcare Center, Floor 3"
    ),
    Provider(
        id="p003",
        name="Dr. Emily Rodriguez",
        specialty=Specialty.CARDIOLOGIST,
        experience_years=20,
        rating=4.9,
        location="789 Heart Institute, Building A"
    ),
    Provider(
        id="p004",
        name="Dr. David Kim",
        specialty=Specialty.NEUROLOGIST,
        experience_years=12,
        rating=4.7,
        location="321 Neurology Center, 2nd Floor"
    ),
    Provider(
        id="p005",
        name="Dr. Jennifer Williams",
        specialty=Specialty.ORTHOPEDIST,
        experience_years=18,
        rating=4.8,
        location="654 Orthopedic Clinic, Suite 100"
    ),
    Provider(
        id="p006",
        name="Dr. Robert Taylor",
        specialty=Specialty.GENERAL_PRACTITIONER,
        experience_years=25,
        rating=4.5,
        location="987 Family Health Center"
    ),
    Provider(
        id="p007",
        name="Dr. Lisa Anderson",
        specialty=Specialty.PEDIATRICIAN,
        experience_years=14,
        rating=4.9,
        location="147 Children's Medical Center"
    ),
    Provider(
        id="p008",
        name="Dr. James Martinez",
        specialty=Specialty.PSYCHIATRIST,
        experience_years=16,
        rating=4.7,
        location="258 Mental Health Associates"
    ),
    Provider(
        id="p009",
        name="Dr. Patricia Brown",
        specialty=Specialty.OPHTHALMOLOGIST,
        experience_years=22,
        rating=4.8,
        location="369 Vision Care Center"
    ),
    Provider(
        id="p010",
        name="Dr. Christopher Lee",
        specialty=Specialty.ENT_SPECIALIST,
        experience_years=10,
        rating=4.6,
        location="741 ENT Clinic, Suite 300"
    ),
]


def get_all_providers() -> List[Provider]:
    """Get all providers."""
    logger.debug(f"[providers.py.get_all_providers] Retrieving all providers (count: {len(PROVIDERS_DB)})")
    return PROVIDERS_DB


def get_provider_by_id(provider_id: str) -> Optional[Provider]:
    """Get a provider by ID."""
    logger.debug(f"[providers.py.get_provider_by_id] Looking up provider: {provider_id}")
    
    for provider in PROVIDERS_DB:
        if provider.id == provider_id:
            logger.debug(f"[providers.py.get_provider_by_id] Provider found: {provider.name}")
            return provider
    
    logger.warning(f"[providers.py.get_provider_by_id] Provider not found: {provider_id}")
    return None


def get_providers_by_specialty(specialty: str) -> List[Provider]:
    """Get providers by specialty."""
    logger.debug(f"[providers.py.get_providers_by_specialty] Searching for providers with specialty: {specialty}")
    
    providers = [p for p in PROVIDERS_DB if p.specialty == specialty]
    logger.debug(f"[providers.py.get_providers_by_specialty] Found {len(providers)} providers with specialty: {specialty}")
    
    return providers


def get_best_provider_for_specialty(specialty: str) -> Optional[Provider]:
    """Get the best-rated provider for a specialty."""
    logger.debug(f"[providers.py.get_best_provider_for_specialty] Finding best provider for specialty: {specialty}")
    
    providers = get_providers_by_specialty(specialty)
    if not providers:
        logger.warning(f"[providers.py.get_best_provider_for_specialty] No providers found for specialty: {specialty}")
        return None
    
    best_provider = max(providers, key=lambda p: (p.rating, p.experience_years))
    logger.info(f"[providers.py.get_best_provider_for_specialty] Best provider for {specialty}: {best_provider.name} (rating: {best_provider.rating})")
    
    return best_provider
