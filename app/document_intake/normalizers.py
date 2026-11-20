import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


def normalize_date(value:str|None)->dict:
    if not value or not value.strip():
        return {
            "raw_date":value,
            "normalized_date":None,
            "status":"MISSING",
            "error":None
        }
    try:
        parsed_date=datetime.strptime(value.strip(),"%d/%m/%Y")
        return {
            "raw_date":value,
            "normalized_date":parsed_date.strftime("%Y-%m-%d"),
            "status":"VALID",
            "error":None
        }
    except ValueError:
        return {
            "raw_date":value,
            "normalized_date":None,
            "status":"INVALID",
            "error":"Invalid calendar date"
        }


def normalize_time(value: str | None) -> dict:
    if value is None or not value.strip():
        return {
            "raw_time": value,
            "normalized_time": None,
            "status": "MISSING",
            "error": None
        }

    try:
        parsed_time = datetime.strptime(
            value.strip().upper(),
            "%I:%M %p"
        )

        return {
            "raw_time": value,
            "normalized_time": parsed_time.strftime("%H:%M"),
            "status": "VALID",
            "error": None
        }

    except ValueError:
        return {
            "raw_time": value,
            "normalized_time": None,
            "status": "INVALID",
            "error": "Invalid time format"
        }

def normalize_currency(value: str | None) -> dict:
    if value is None or not value.strip():
        return {
            "raw_amount": value,
            "normalized_amount": None,
            "status": "MISSING",
            "error": None
        }

    try:
        cleaned = value.strip()

        # Accept Rs., Rs, INR and ₹ prefixes
        cleaned = re.sub(
            r"^(?:Rs\.?|INR|₹)\s*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        # Validate comma grouping before removing commas
        amount_pattern = (
            r"(?:\d+|\d{1,3}(?:,\d{2})*,\d{3})"
            r"(?:\.\d{1,2})?"
        )

        if not re.fullmatch(amount_pattern, cleaned):
            raise ValueError("Invalid currency format")

        normalized = Decimal(cleaned.replace(",", ""))

        return {
            "raw_amount": value,
            "normalized_amount": normalized,
            "status": "VALID",
            "error": None
        }

    except (ValueError, InvalidOperation):
        return {
            "raw_amount": value,
            "normalized_amount": None,
            "status": "INVALID",
            "error": "Invalid currency amount"
        }


def normalize_registration(value: str | None) -> dict:
    if value is None or not value.strip():
        return {
            "raw_registration": value,
            "normalized_registration": None,
            "status": "MISSING",
            "error": None
        }

    cleaned = re.sub(
        r"[\s-]+",
        "",
        value.strip()
    ).upper()

    # Basic Indian registration format (MVP)
    pattern = r"[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{1,4}"

    if not re.fullmatch(pattern, cleaned):
        return {
            "raw_registration": value,
            "normalized_registration": None,
            "status": "INVALID",
            "error": "Invalid vehicle registration format"
        }

    return {
        "raw_registration": value,
        "normalized_registration": cleaned,
        "status": "VALID",
        "error": None
    }


def normalize_text(value: str | None) -> dict:
    if value is None or not value.strip():
        return {
            "raw_text": value,
            "normalized_text": None,
            "status": "MISSING",
            "error": None
        }

    cleaned = " ".join(value.split())

    return {
        "raw_text": value,
        "normalized_text": cleaned,
        "status": "VALID",
        "error": None
    }