"""
Provider matching logic using LLM and rules-based approach.
"""
import logging
from typing import Optional, List
from backend.models.schemas import Provider, ProviderMatch
from backend.models.constants import ISSUE_TO_SPECIALTY, Specialty
from backend.database.providers import get_providers_by_specialty, get_best_provider_for_specialty

logger = logging.getLogger(__name__)


def match_provider_for_issue(health_issue: str) -> Optional[ProviderMatch]:
    """
    Match the best provider for a health issue.
    
    This uses a rule-based approach with keyword matching to determine
    the appropriate specialty, then selects the best-rated provider.
    
    Args:
        health_issue: Description of the patient's health issue
        
    Returns:
        ProviderMatch object or None if no match found
    """
    logger.info(f"[provider_matcher.py.match_provider_for_issue] Matching provider for health issue: {health_issue}")
    
    health_issue_lower = health_issue.lower()
    
    # Try to find matching specialty from keywords
    matched_specialty = None
    match_keyword = None
    
    for keyword, specialty in ISSUE_TO_SPECIALTY.items():
        if keyword in health_issue_lower:
            matched_specialty = specialty
            match_keyword = keyword
            logger.debug(f"[provider_matcher.py.match_provider_for_issue] Matched keyword '{keyword}' to specialty: {specialty}")
            break
    
    # If no specific match, default to general practitioner
    if not matched_specialty:
        matched_specialty = Specialty.GENERAL_PRACTITIONER
        match_reason = "No specific specialty identified, recommending general practitioner for initial evaluation"
        confidence = 0.6
        logger.info(f"[provider_matcher.py.match_provider_for_issue] No specific match found, defaulting to general practitioner")
    else:
        match_reason = f"Identified '{match_keyword}' in health issue, recommending {matched_specialty}"
        confidence = 0.9
        logger.info(f"[provider_matcher.py.match_provider_for_issue] Matched specialty: {matched_specialty} (confidence: {confidence})")
    
    # Get the best provider for this specialty
    provider = get_best_provider_for_specialty(matched_specialty)
    
    if not provider:
        logger.warning(f"[provider_matcher.py.match_provider_for_issue] No provider found for specialty: {matched_specialty}")
        return None
    
    logger.info(f"[provider_matcher.py.match_provider_for_issue] Selected provider: {provider.name} (ID: {provider.id})")
    
    return ProviderMatch(
        provider_id=provider.id,
        provider_name=provider.name,
        specialty=provider.specialty,
        match_reason=match_reason,
        confidence=confidence
    )


def get_multiple_provider_options(health_issue: str, max_results: int = 3) -> List[ProviderMatch]:
    """
    Get multiple provider options for a health issue.
    
    Args:
        health_issue: Description of the patient's health issue
        max_results: Maximum number of providers to return
        
    Returns:
        List of ProviderMatch objects
    """
    logger.info(f"[provider_matcher.py.get_multiple_provider_options] Getting multiple provider options for: {health_issue} (max: {max_results})")
    
    health_issue_lower = health_issue.lower()
    
    # Find matching specialty
    matched_specialty = None
    for keyword, specialty in ISSUE_TO_SPECIALTY.items():
        if keyword in health_issue_lower:
            matched_specialty = specialty
            logger.debug(f"[provider_matcher.py.get_multiple_provider_options] Matched specialty: {specialty}")
            break
    
    if not matched_specialty:
        matched_specialty = Specialty.GENERAL_PRACTITIONER
        logger.info(f"[provider_matcher.py.get_multiple_provider_options] No specific match, using general practitioner")
    
    # Get all providers for this specialty
    providers = get_providers_by_specialty(matched_specialty)
    logger.debug(f"[provider_matcher.py.get_multiple_provider_options] Found {len(providers)} providers for specialty: {matched_specialty}")
    
    # Sort by rating and experience
    providers.sort(key=lambda p: (p.rating, p.experience_years), reverse=True)
    
    # Create ProviderMatch objects
    matches = []
    for i, provider in enumerate(providers[:max_results]):
        confidence = 0.9 - (i * 0.1)  # Slightly lower confidence for subsequent matches
        matches.append(ProviderMatch(
            provider_id=provider.id,
            provider_name=provider.name,
            specialty=provider.specialty,
            match_reason=f"Specialty match for {matched_specialty}",
            confidence=confidence
        ))
        logger.debug(f"[provider_matcher.py.get_multiple_provider_options] Added provider option: {provider.name} (confidence: {confidence})")
    
    logger.info(f"[provider_matcher.py.get_multiple_provider_options] Returning {len(matches)} provider options")
    return matches
