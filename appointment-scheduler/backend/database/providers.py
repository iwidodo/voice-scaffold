"""
CSV-based provider database.
Loads provider data from CSV file on startup and maintains it in-memory for fast queries.
"""
import logging
import csv
from pathlib import Path
from typing import List, Optional
from backend.models.schemas import Provider

logger = logging.getLogger(__name__)

# In-memory provider database (loaded from CSV)
PROVIDERS_DB: List[Provider] = []

# Path to the CSV file
CSV_FILE = Path(__file__).parent / "providers.csv"


def load_providers_from_csv() -> List[Provider]:
    """
    Load providers from CSV file.
    
    Returns:
        List of Provider objects
    """
    providers = []
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                provider = Provider(
                    id=row['id'],
                    name=row['name'],
                    specialty=row['specialty'],
                    experience_years=int(row['experience_years']),
                    rating=float(row['rating']),
                    location=row['location']
                )
                providers.append(provider)
        
        logger.info(f"[providers.py.load_providers_from_csv] Loaded {len(providers)} providers from CSV")
    except FileNotFoundError:
        logger.error(f"[providers.py.load_providers_from_csv] CSV file not found: {CSV_FILE}")
    except Exception as e:
        logger.error(f"[providers.py.load_providers_from_csv] Error loading CSV: {e}")
    
    return providers


def initialize_database():
    """Initialize the provider database by loading from CSV."""
    global PROVIDERS_DB
    PROVIDERS_DB = load_providers_from_csv()
    logger.info(f"[providers.py.initialize_database] Database initialized with {len(PROVIDERS_DB)} providers")


# Initialize on module load
initialize_database()


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
