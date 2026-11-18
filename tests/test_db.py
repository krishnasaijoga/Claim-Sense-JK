from app.db import get_policy, get_prior_claims


import sqlite3
from unittest.mock import patch, MagicMock
import pytest

from app.db import get_policy


def locked_error():
    error = sqlite3.OperationalError("database is locked")
    error.sqlite_errorcode = sqlite3.SQLITE_BUSY
    return error

# Test 1: First attempt fails, second succeeds
@patch("app.db.time.sleep")
@patch("app.db.connect")
def test_get_policy_retry_then_success(mock_connect, mock_sleep):
    mock_conn = MagicMock()
    mock_conn.execute.side_effect = [
        locked_error(),
        MagicMock(fetchone=lambda: {
            "policy_number": "NS-MOT-240101"
        })
    ]
    mock_connect.return_value = mock_conn

    result = get_policy("NS-MOT-240101", max_retries=3, base_delay=0.5)

    assert result["policy_number"] == "NS-MOT-240101" # type: ignore
    assert mock_connect.call_count == 2
    assert mock_conn.execute.call_count == 2
    mock_sleep.assert_called_once_with(0.5)


# Test 2: All retry attempts fail
@patch("app.db.time.sleep")
@patch("app.db.connect")
def test_get_policy_retry_exhausted(mock_connect, mock_sleep):
    mock_conn = MagicMock()
    mock_conn.execute.side_effect = locked_error()
    mock_connect.return_value = mock_conn

    with pytest.raises(sqlite3.OperationalError):
        get_policy("NS-MOT-240101", max_retries=3, base_delay=0.5)

    assert mock_connect.call_count == 3
    assert mock_conn.execute.call_count == 3
    assert mock_sleep.call_count == 2


# Test 3: Non-retryable database error
@patch("app.db.time.sleep")
@patch("app.db.connect")
def test_get_policy_non_retryable_error(mock_connect, mock_sleep):
    mock_conn = MagicMock()
    mock_conn.execute.side_effect = sqlite3.OperationalError(
        "no such table: policies"
    )
    mock_connect.return_value = mock_conn

    with pytest.raises(sqlite3.OperationalError):
        get_policy("NS-MOT-240101", max_retries=3)

    assert mock_connect.call_count == 1
    mock_sleep.assert_not_called()


# Test 4: Invalid retry parameters
@pytest.mark.parametrize(
    "max_retries, base_delay",
    [
        (0, 0.5),
        (-1, 0.5),
        (3, -0.5),
    ]
)
def test_get_policy_invalid_retry_parameters(max_retries, base_delay):
    with pytest.raises(ValueError):
        get_policy(
            "NS-MOT-240101",
            max_retries=max_retries,
            base_delay=base_delay
        )



def test_valid_policy_returns_dict():
    rows=get_policy("NS-MOT-240101")
    assert rows is not None
    assert isinstance(rows,dict)
    assert rows["policy_number"]=="NS-MOT-240101"


def test_unknown_policy_number_returns_none():
    rows=get_policy("NS-MOT-240100")
    assert rows is None


def test_policy_claims_under_12_month_window():
    count=get_prior_claims("NS-MOT-240109","2026-11-18")
    assert count==2


def test_policy_with_no_prior_claims_window():
    count=get_prior_claims("NS-MOT-240102","2026-11-18")
    assert count==0


def test_prior_claim_inclusive_12_month_boundary():
    count=get_prior_claims("NS-MOT-240103","2026-03-02")
    assert count==1
    count=get_prior_claims("NS-MOT-240103","2027-03-03")
    assert count==0