from pypdf import PdfReader

from app.document_intake.label_parser import find_labels


# Step 1: Define the labels we want to recognize
LABEL_PATTERNS = {
    "policy_number": r"Policy\s+number",
    "insured_name": r"Insured\s+name",
    "accident_date": r"Date\s+of\s+accident",
    "accident_time": r"Time\s+of\s+accident",
    "accident_place": r"Place\s+of\s+accident",
    "accident_description": r"How\s+did\s+the\s+accident\s+happen\?",
    "damaged_parts": r"Damaged\s+parts\s+\(as\s+per\s+insured\)",
    "driver_name": r"Driver\s+name",
    "garage": r"Garage\s+code\s*/\s*name",
    "garage_estimate": r"Garage\s+repair\s+estimate",
}

# Labels that mark a boundary but aren't data fields
BOUNDARY_PATTERNS = {
    "_claim_reference": r"Claim\s+reference:",
    "_mobile": r"Mobile",
    "_vehicle_registration": r"Vehicle\s+registration\s+no\.",
    "_make_model": r"Make\s*/\s*model",
    "_licence_number": r"Driving\s+licence\s+no\.",
    "_licence_validity": r"Licence\s+valid\s+till",
    "_fir": r"FIR\s+filed\?",
    "_witness": r"Witness\s+available\?",
    "_section_a": r"A\.\s+Policy\s+and\s+vehicle",
    "_section_b": r"B\.\s+Accident\s+details",
    "_section_c": r"C\.\s+Driver\s+details",
    "_section_d": r"D\.\s+Police,\s+witness\s+and\s+garage",
    "_declaration": r"I\s+declare\s+that\s+the\s+information",
}


# Step 2: Extract values between consecutive labels
def parse_claim_fields(text: str) -> dict[str, str | None]:
    labels=find_labels(text,LABEL_PATTERNS)

    result = {field: None for field in LABEL_PATTERNS}

    for i, current in enumerate(labels):
        field = current["field"]

        # Ignore section markers and other boundary-only labels
        if field not in result:
            continue

        start = current["end"]

        if i + 1 < len(labels):
            end = labels[i + 1]["start"]
        else:
            end = len(text)

        value = " ".join(text[start:end].split())

        if value:
            result[field] = value # type: ignore

    return result # type: ignore


def diagnose_missing_field(
    text: str,
    field: str,
    extracted_value: str | None
) -> str:

    # Field extracted successfully
    if extracted_value is not None:
        return "EXTRACTED"

    # Check whether the field label was recognized
    labels=find_labels(text,LABEL_PATTERNS)

    label_found = any(
        item["field"] == field
        for item in labels
    )

    if label_found:
        for i, item in enumerate(labels):
            if item["field"] == field:
                current_label_end = item["end"]

                # Find the next recognized label
                if i + 1 < len(labels):
                    next_label_start = labels[i + 1]["start"]
                else:
                    next_label_start = len(text)

                # Extract text between the two labels
                value = text[current_label_end:next_label_start].strip()

                if not value:
                    return "EMPTY_VALUE"

                return "LABEL_PRESENT_EXTRACTION_FAILED"

    # Secondary diagnostic check using normalized text
    diagnostic_labels = {
        "accident_description": "how did the accident happen?",
        "accident_date": "date of accident",
        "policy_number": "policy number"
    }

    expected_label = diagnostic_labels.get(field)

    if expected_label:
        normalized_text = " ".join(text.lower().split())

        if expected_label in normalized_text:
            return "LABEL_PRESENT_EXTRACTION_FAILED"

    return "LABEL_NOT_FOUND"


# Step 4: Read PDF and parse its contents
def parser_claim_form(path: str) -> dict:
    reader = PdfReader(path)

    text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    extracted_fields = parse_claim_fields(text)

    diagnostics = {
        field: diagnose_missing_field(
            text=text,
            field=field,
            extracted_value=value
        )
        for field, value in extracted_fields.items()
    }

    return {
        "data": extracted_fields,
        "diagnostics": diagnostics
    }


if __name__ == "__main__":
    path = "./data/sample_claims/CLM-1006/claim_form.pdf"

    output = parser_claim_form(path)

    for key, value in output.items():
        print(f"{key}: {value}")
