"""
Tests for provider matcher.
"""
import pytest
from backend.llm.provider_matcher import (
    match_provider_for_issue,
    get_multiple_provider_options
)
from backend.models.constants import Specialty


def test_match_dermatologist():
    """Test matching for skin issues."""
    result = match_provider_for_issue("I have a rash on my arm")
    assert result is not None
    assert result.specialty == Specialty.DERMATOLOGIST
    assert result.confidence > 0.5


def test_match_neurologist():
    """Test matching for neurological issues."""
    result = match_provider_for_issue("I have severe headaches")
    assert result is not None
    assert result.specialty == Specialty.NEUROLOGIST
    assert result.confidence > 0.5


def test_match_cardiologist():
    """Test matching for heart issues."""
    result = match_provider_for_issue("I have chest pain")
    assert result is not None
    assert result.specialty == Specialty.CARDIOLOGIST


def test_match_orthopedist():
    """Test matching for bone/joint issues."""
    result = match_provider_for_issue("I have back pain")
    assert result is not None
    assert result.specialty == Specialty.ORTHOPEDIST


def test_match_general_practitioner_fallback():
    """Test fallback to general practitioner for unspecified issues."""
    result = match_provider_for_issue("I don't feel well")
    assert result is not None
    assert result.specialty == Specialty.GENERAL_PRACTITIONER
    assert result.confidence < 0.9  # Lower confidence for general issues


def test_multiple_provider_options():
    """Test getting multiple provider options."""
    results = get_multiple_provider_options("I have a rash", max_results=2)
    assert len(results) > 0
    assert len(results) <= 2
    assert all(r.specialty == Specialty.DERMATOLOGIST for r in results)
    # First result should have higher confidence
    if len(results) > 1:
        assert results[0].confidence >= results[1].confidence


def test_provider_match_has_valid_data():
    """Test that provider match has all required data."""
    result = match_provider_for_issue("I have acne")
    assert result is not None
    assert result.provider_id
    assert result.provider_name
    assert result.specialty
    assert result.match_reason
    assert 0 <= result.confidence <= 1
