

import pytest
from decimal import Decimal

from app.document_intake.normalizers import (
    normalize_time,
    normalize_currency,
    normalize_registration,
    normalize_text,
    normalize_date
)


@pytest.mark.parametrize(
    "raw, expected, status",
    [
        ("9:10 PM", "21:10", "VALID"),
        ("9:10 AM", "09:10", "VALID"),
        ("12:00 AM", "00:00", "VALID"),
        ("12:00 PM", "12:00", "VALID"),
        ("11:59 PM", "23:59", "VALID"),
        ("25:30 PM", None, "INVALID"),
        ("13:10 PM", None, "INVALID"),
        ("9:70 AM", None, "INVALID"),
        (None, None, "MISSING"),
        ("", None, "MISSING"),
        ("   ", None, "MISSING"),
    ]
)
def test_normalize_time(raw, expected, status):
    result = normalize_time(raw)

    assert result["raw_time"] == raw
    assert result["normalized_time"] == expected
    assert result["status"] == status


@pytest.mark.parametrize(
    "raw, expected, status",
    [
        ("Rs. 47,000", Decimal("47000"), "VALID"),
        ("INR 125000", Decimal("125000"), "VALID"),
        ("₹1,25,000", Decimal("125000"), "VALID"),
        ("Rs. 12,500.50", Decimal("12500.50"), "VALID"),
        ("45000", Decimal("45000"), "VALID"),
        ("47,00,000", Decimal("4700000"), "VALID"),
        ("Rs. ABC", None, "INVALID"),
        ("12,34,56", None, "INVALID"),
        ("-5000", None, "INVALID"),
        (None, None, "MISSING"),
        ("", None, "MISSING"),
        ("   ", None, "MISSING"),
    ]
)
def test_normalize_currency(raw, expected, status):
    result = normalize_currency(raw)

    assert result["raw_amount"] == raw
    assert result["normalized_amount"] == expected
    assert result["status"] == status


@pytest.mark.parametrize(
    "raw, expected, status",
    [
        ("MH-02-FG-9001", "MH02FG9001", "VALID"),
        ("mh 02 fg 9001", "MH02FG9001", "VALID"),
        ("KA-03-MN-1234", "KA03MN1234", "VALID"),
        ("MH-02-FG-9001 (XUV700)", None, "INVALID"),
        ("INVALID123", None, "INVALID"),
        (None, None, "MISSING"),
        ("", None, "MISSING"),
    ]
)
def test_normalize_registration(raw, expected, status):
    result = normalize_registration(raw)

    assert result["normalized_registration"] == expected
    assert result["status"] == status


def test_normalize_text():
    result = normalize_text(
        "Vehicle   was hit\nfrom   behind."
    )

    assert result["normalized_text"] == (
        "Vehicle was hit from behind."
    )
    assert result["status"] == "VALID"


def test_normalize_text_missing():
    result = normalize_text("   ")

    assert result["normalized_text"] is None
    assert result["status"] == "MISSING"


@pytest.mark.parametrize(
    "raw, expected, status",
    [
        ("30/10/2026", "2026-10-30", "VALID"),
        ("01/01/2026", "2026-01-01", "VALID"),
        ("29/02/2024", "2024-02-29", "VALID"),
        ("29/02/2025", None, "INVALID"),
        ("31/02/2026", None, "INVALID"),
        ("32/10/2026", None, "INVALID"),
        ("30/13/2026", None, "INVALID"),
        ("2026-10-30", None, "INVALID"),
        (None, None, "MISSING"),
        ("", None, "MISSING"),
        ("   ", None, "MISSING"),
    ]
)
def test_normalize_date(raw, expected, status):
    result = normalize_date(raw)

    assert result["raw_date"] == raw
    assert result["normalized_date"] == expected
    assert result["status"] == status

    if status == "INVALID":
        assert result["error"] is not None
    else:
        assert result["error"] is None
