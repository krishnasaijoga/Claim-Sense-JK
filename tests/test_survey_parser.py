
from pathlib import Path

from app.document_intake.survey_parser import (
    parse_survey_form,
    parse_survey_text,
)


# Test 1: Real CLM-1006 survey PDF
def test_survey_valid_total():
    path = Path(
        "data/sample_claims/CLM-1006/survey_report.pdf"
    )

    result = parse_survey_form(str(path))

    assert len(result["line_items"]) == 4
    assert result["calculated_total"] == 45000
    assert result["reported_total"] == 45000
    assert result["table_valid"] is True


# Reusable synthetic survey text
VALID_SURVEY_TEXT = """
Assessment of loss
S.No
Description
Category
Assessed amount
1
Rear bumper
Plastic/Rubber
Rs. 12,000
2
Right tail lamp
Plastic/Rubber
Rs. 9,500
3
Tailgate
Metal
Rs. 15,000
4
Labour and painting
Labour
Rs. 8,500
Total assessed (before depreciation)
Rs. 45,000
"""


# Test 2: Incorrect reported total
def test_survey_total_mismatch():
    modified_text = VALID_SURVEY_TEXT.replace(
        "Rs. 45,000",
        "Rs. 44,000"
    )

    result = parse_survey_text(modified_text)

    assert result["calculated_total"] == 45000
    assert result["reported_total"] == 44000
    assert result["table_valid"] is False


# Test 3: Missing serial number
def test_survey_missing_serial_number():
    modified_text = VALID_SURVEY_TEXT.replace(
        "3\nTailgate",
        "5\nTailgate"
    )

    result = parse_survey_text(modified_text)

    assert result["table_valid"] is False


# Test 4: Reported total missing
def test_survey_reported_total_missing():
    modified_text = VALID_SURVEY_TEXT.replace(
        "Rs. 45,000",
        ""
    )

    result = parse_survey_text(modified_text)

    assert result["reported_total"] is None
    assert result["table_valid"] is False


# Test 5: Row omitted from extracted text
def test_survey_missing_line_item():
    modified_text = VALID_SURVEY_TEXT.replace(
        "3\nTailgate\nMetal\nRs. 15,000\n",
        ""
    )

    result = parse_survey_text(modified_text)

    assert len(result["line_items"]) == 3
    assert result["calculated_total"] == 30000
    assert result["reported_total"] == 45000
    assert result["table_valid"] is False


# Test 6: No line items
def test_survey_empty_table():
    text = """
Assessment of loss
S.No
Description
Category
Assessed amount
Total assessed (before depreciation)
Rs. 45,000
"""

    result = parse_survey_text(text)

    assert result["line_items"] == []
    assert result["table_valid"] is False
