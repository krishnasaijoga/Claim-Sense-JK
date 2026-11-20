
from pathlib import Path
from app.document_intake.claim_parser import parser_claim_form
from app.document_intake.survey_parser import parse_survey_form
from app.document_intake.fir_parser import parse_fir_form

CLAIMS_PARENT_DIR = Path("./data/sample_claims")

TARGET_CLAIM_FILE_NAME = "claim_form.pdf"
TARGET_SURVEY_FILE_NAME = "survey_report.pdf"
TARGET_FIR_FILE_NAME = "fir.pdf"

REQUIRED_CLAIMS_FIELDS = {
    "policy_number",
    "accident_date",
    "accident_description",
}

REQUIRED_SURVEY_FIELDS={
    "claim_number",
    "line_items",
    "estimated_total",
    "calculated_total",
    "table_valid"
}


def batch_process_claims(path: Path) -> list[dict]:
    claims_batch = []

    for folder in sorted(path.iterdir()):

        if not folder.is_dir():
            continue

        claim_id = folder.name
        file_path = folder / TARGET_CLAIM_FILE_NAME

        if not file_path.is_file():
            claims_batch.append({
                "claim_id": claim_id,
                "status": "FAILED",
                "missing_fields": [],
                "error": "Claim form PDF not found",
            })
            continue

        try:
            parsed_claim = parser_claim_form(str(file_path))

            # Current parser returns:
            # {"data": {...}, "diagnostics": {...}}
            data = parsed_claim["data"]

            missing_fields = [
                field
                for field in REQUIRED_CLAIMS_FIELDS
                if data.get(field) is None
            ]

            status = "PARTIAL" if missing_fields else "SUCCESS"

            claims_batch.append({
                "claim_id": claim_id,
                "status": status,
                "missing_fields": sorted(missing_fields),
                "error": None,
                "data": data,
                "diagnostics": parsed_claim["diagnostics"],
            })

        except Exception as exc:
            claims_batch.append({
                "claim_id": claim_id,
                "status": "FAILED",
                "missing_fields": [],
                "error": str(exc),
            })

    return claims_batch



def batch_process_surveys(path: Path) -> list[dict]:
    surveys_batch = []

    for folder in sorted(path.iterdir()):

        if not folder.is_dir():
            continue

        claim_id = folder.name
        file_path = folder / TARGET_SURVEY_FILE_NAME

        # Case 1: Survey PDF missing
        if not file_path.is_file():
            surveys_batch.append({
                "claim_id": claim_id,
                "status": "FAILED",
                "line_item_count": 0,
                "calculated_total": None,
                "reported_total": None,
                "table_valid": False,
                "error": "Survey report PDF not found",
            })
            continue

        try:
            parsed_survey = parse_survey_form(str(file_path))

            line_items = parsed_survey["line_items"]
            table_valid = parsed_survey["table_valid"]

            # A readable report may still contain invalid data
            status = "SUCCESS" if table_valid else "PARTIAL"

            surveys_batch.append({
                "claim_id": claim_id,
                "status": status,
                "line_item_count": len(line_items),
                "calculated_total": parsed_survey["calculated_total"],
                "reported_total": parsed_survey["reported_total"],
                "table_valid": table_valid,
                "error": None,
            })

        except Exception as exc:
            # Isolate failures to individual claims
            surveys_batch.append({
                "claim_id": claim_id,
                "status": "FAILED",
                "line_item_count": 0,
                "calculated_total": None,
                "reported_total": None,
                "table_valid": False,
                "error": str(exc),
            })

    return surveys_batch


def batch_process_firs(path: Path) -> list[dict]:
    firs_batch = []

    for folder in sorted(path.iterdir()):

        if not folder.is_dir():
            continue

        claim_id = folder.name
        file_path = folder / TARGET_FIR_FILE_NAME

        try:
            parsed_fir = parse_fir_form(str(file_path))

            fir_status = parsed_fir["fir_status"]

            # Preserve all extracted FIR information
            fir_data = {
                key: value
                for key, value in parsed_fir.items()
                if key not in ("fir_status", "error")
            }

            firs_batch.append({
                "claim_id": claim_id,
                "fir_status": fir_status,
                "data": fir_data if fir_status in ("SUCCESS", "PARTIAL") else None,
                "error": parsed_fir.get("error")
            })

        except Exception as exc:
            firs_batch.append({
                "claim_id": claim_id,
                "fir_status": "FAILED",
                "data": None,
                "error": str(exc)
            })

    return firs_batch