
from pathlib import Path

from app.document_intake.fir_parser import (
    parse_fir_fields,
    parse_fir_form,
    get_fir_status,
)


VALID_FIR_TEXT = """
FIR number
AND/2026/1187
Police station
Andheri Police Station
Date of incident
30/10/2026
Time of incident
9:10 PM
Place of incident
Andheri East, Mumbai
Vehicle involved
MH-02-FG-9001
Breath analyser result (driver of insured vehicle)
Negative
Brief facts
The insured vehicle was hit from behind by a taxi.
"""


# Test 1: Extract all FIR fields
def test_valid_fir_extraction():
    result = parse_fir_fields(VALID_FIR_TEXT)

    assert result["fir_number"] == "AND/2026/1187"
    assert result["police_station"] == "Andheri Police Station"
    assert result["date_of_incident"] == "30/10/2026"
    assert result["time_of_incident"] == "9:10 PM"
    assert result["place_of_incident"] == "Andheri East, Mumbai"
    assert result["vehicle_involved"] == "MH-02-FG-9001"
    assert result["breath_analyser_result"] == "Negative"
    assert result["brief_facts"] == (
        "The insured vehicle was hit from behind by a taxi."
    )


# Test 2: Multiline breath analyser heading
def test_multiline_breath_analyser():
    text = """
Breath analyser result (driver
of insured vehicle)
Positive - 78 mg/100 ml
Brief facts
Driver was stopped for investigation.
"""

    result = parse_fir_fields(text)

    assert result["breath_analyser_result"] == (
        "Positive - 78 mg/100 ml"
    )


# Test 3: Preserve an explicitly recorded "Not tested"
def test_breath_analyser_not_tested():
    text = """
Breath analyser result (driver of insured vehicle)
Not tested
Brief facts
The complainant was not at fault.
"""

    result = parse_fir_fields(text)

    assert result["breath_analyser_result"] == "Not tested"
    assert result["brief_facts"] == (
        "The complainant was not at fault."
    )


# Test 4: Missing breath analyser field
def test_missing_breath_analyser():
    text = """
FIR number
AND/2026/1187
Vehicle involved
MH-02-FG-9001
Brief facts
A taxi hit the insured vehicle.
"""

    result = parse_fir_fields(text)

    assert result["breath_analyser_result"] is None
    assert result["fir_number"] == "AND/2026/1187"
    assert result["brief_facts"] == (
        "A taxi hit the insured vehicle."
    )


# Test 5: All required FIR fields present
def test_fir_status_success():
    data = parse_fir_fields(VALID_FIR_TEXT)

    assert get_fir_status(data) == "SUCCESS"


# Test 6: Missing required field produces PARTIAL
def test_fir_status_partial():
    data = parse_fir_fields(VALID_FIR_TEXT)
    data["breath_analyser_result"] = None

    assert get_fir_status(data) == "PARTIAL"


# Test 7: Explicit "Not tested" is not missing
def test_not_tested_is_success():
    data = parse_fir_fields(VALID_FIR_TEXT)
    data["breath_analyser_result"] = "Not tested"

    assert get_fir_status(data) == "SUCCESS"


# Test 8: Real CLM-1006 FIR
def test_real_fir_clm_1006():
    path = Path("data/sample_claims/CLM-1006/fir.pdf")

    result = parse_fir_form(str(path))

    assert result["fir_number"] == "AND/2026/1187"
    assert result["date_of_incident"] == "30/10/2026"
    assert "MH-02-FG-9001" in result["vehicle_involved"]
    assert result["breath_analyser_result"] is not None
    assert result["brief_facts"] is not None
    assert result["fir_status"] == "SUCCESS"


# Test 9: Real CLM-1014 FIR
def test_real_fir_clm_1014():
    path = Path("data/sample_claims/CLM-1014/fir.pdf")

    result = parse_fir_form(str(path))

    assert "78 mg/100 ml" in result["breath_analyser_result"]
    assert result["brief_facts"] is not None
    assert result["fir_status"] == "SUCCESS"


# Test 10: Missing FIR file
def test_missing_fir_file(tmp_path):
    path = tmp_path / "missing_fir.pdf"

    result = parse_fir_form(str(path))

    assert result == {
        "fir_status": "NOT_PROVIDED"
    }



# Test 11: Corrupted PDF
def test_corrupted_fir_returns_failed(tmp_path):
    file_path = tmp_path / "corrupted_fir.pdf"
    file_path.write_bytes(b"This is not a valid PDF file")

    result = parse_fir_form(str(file_path))

    assert result["fir_status"] == "FAILED"
    assert "error" in result


# Test 12: Readable PDF with missing required fields
def test_incomplete_fir_returns_partial(tmp_path):
    from pypdf import PdfWriter

    file_path = tmp_path / "empty_fir.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)

    with file_path.open("wb") as f:
        writer.write(f)

    result = parse_fir_form(str(file_path))

    assert result["fir_status"] == "PARTIAL"
    assert result["fir_number"] is None
    assert result["breath_analyser_result"] is None
