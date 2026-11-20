
from app.document_intake.claim_parser import (
    parse_claim_fields,
    diagnose_missing_field,
)


def test_valid_accident_description():
    text = """
How did the accident happen?
Car was hit from behind.
Damaged parts (as per insured)
Rear bumper
"""
    result = parse_claim_fields(text)

    assert result["accident_description"] == "Car was hit from behind."
    assert diagnose_missing_field(
        text, "accident_description",
        result["accident_description"]
    ) == "EXTRACTED"


def test_missing_accident_description_label():
    text = """
Date of accident
30/10/2026
Time of accident
9:10 PM
"""

    result = parse_claim_fields(text)

    assert result["accident_description"] is None
    assert diagnose_missing_field(
        text, "accident_description",
        result["accident_description"]
    ) == "LABEL_NOT_FOUND"


def test_empty_accident_description():
    text = """
How did the accident happen?
Damaged parts (as per insured)
Rear bumper
"""

    result = parse_claim_fields(text)

    assert result["accident_description"] is None

    assert diagnose_missing_field(
        text, "accident_description",
        result["accident_description"]
    ) == "EMPTY_VALUE"


def test_multiline_accident_description():
    text = """
How did the accident
happen?
Car was hit from behind.
Rear bumper was damaged.
Damaged parts (as per
insured)
Rear bumper
"""

    result = parse_claim_fields(text)

    assert result["accident_description"] == (
        "Car was hit from behind. Rear bumper was damaged."
    )


def test_label_present_but_extraction_failed():
    text = """
How did the accident happen?
Car was hit from behind.
Damaged parts (as per insured)
Rear bumper
"""

    # Simulate a parser failure despite the source containing a value
    assert diagnose_missing_field(
        text,
        "accident_description",
        None
    ) == "LABEL_PRESENT_EXTRACTION_FAILED"


def test_field_order_changed():
    text = """
Time of accident
9:10 PM
Date of accident
30/10/2026
Place of accident
Mumbai
"""

    result = parse_claim_fields(text)

    assert result["accident_time"] == "9:10 PM"
    assert result["accident_date"] == "30/10/2026"
    assert result["accident_place"] == "Mumbai"
