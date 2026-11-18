
import sqlite3
from unittest.mock import patch
from app.services import get_policy_context


# Test 1: Both lookups succeed
@patch("app.services.get_prior_claims")
@patch("app.services.get_policy")
def test_policy_context_success(mock_policy, mock_prior_claims):
    mock_policy.return_value = {
        "policy_number": "NS-MOT-240101",
        "policy_type": "COMPREHENSIVE",
        "idv": 500000
    }
    mock_prior_claims.return_value = 2

    result = get_policy_context(
        "NS-MOT-240101", "2026-11-18"
    )

    assert result["status"] == "SUCCESS"
    assert result["policy_number"] == "NS-MOT-240101"
    assert result["idv"] == 500000
    assert result["prior_claims_count"] == 2

    mock_policy.assert_called_once_with(
        policy_number="NS-MOT-240101"
    )
    mock_prior_claims.assert_called_once_with(
        policy_number="NS-MOT-240101",
        reference_date="2026-11-18"
    )


# Test 2: Policy doesn't exist
@patch("app.services.get_prior_claims")
@patch("app.services.get_policy")
def test_policy_not_found(mock_policy, mock_prior_claims):
    mock_policy.return_value = None

    result = get_policy_context(
        "NS-MOT-999999", "2026-11-18"
    )

    assert result["status"] == "POLICY_NOT_FOUND"
    assert result["policy_number"] == "NS-MOT-999999"

    mock_prior_claims.assert_not_called()


# Test 3: Policy lookup database failure
@patch("app.services.get_prior_claims")
@patch("app.services.get_policy")
def test_policy_lookup_unavailable(mock_policy, mock_prior_claims):
    mock_policy.side_effect = sqlite3.OperationalError(
        "database is locked"
    )

    result = get_policy_context(
        "NS-MOT-240101", "2026-11-18"
    )

    assert result["status"] == "POLICY_LOOKUP_UNAVAILABLE"
    assert result["policy_number"] == "NS-MOT-240101"
    assert "error" in result

    mock_prior_claims.assert_not_called()


# Test 4: Prior claims lookup fails
@patch("app.services.get_prior_claims")
@patch("app.services.get_policy")
def test_prior_claims_unavailable(mock_policy, mock_prior_claims):
    mock_policy.return_value = {
        "policy_number": "NS-MOT-240101",
        "policy_type": "COMPREHENSIVE",
        "idv": 500000
    }

    mock_prior_claims.side_effect = sqlite3.OperationalError(
        "database is locked"
    )

    result = get_policy_context(
        "NS-MOT-240101", "2026-11-18"
    )

    assert result["status"] == "PRIOR_CLAIMS_UNAVAILABLE"

    # Preserve retrieved policy information
    assert result["policy_number"] == "NS-MOT-240101"
    assert result["idv"] == 500000

    # Never silently substitute zero
    assert result["prior_claims_count"] is None
    assert "error" in result
