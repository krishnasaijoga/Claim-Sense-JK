import re
from pypdf import PdfReader


ROW_PATTERN = re.compile(
    r"(?m)^\s*(\d+)\s*\n"
    r"([^\n]+)\n"
    r"(Plastic/Rubber|Metal|Glass|Labour)\n"
    r"Rs\.\s*([\d,]+)\s*$",
    re.IGNORECASE
)

FINAL_ROW_PATTERN = re.compile(
    r"Total\s+assessed\s+\(before\s+depreciation\)"
    r"\s*Rs\.\s*([\d,]+)",
    re.IGNORECASE
)

def parse_survey_text(text: str) -> dict:
    rows = []

    for match in ROW_PATTERN.finditer(text):
        rows.append({
            "serial_number": int(match.group(1)),
            "description": match.group(2).strip(),
            "category": match.group(3).strip(),
            "assessed_amount": int(
                match.group(4).replace(",", "")
            )
        })

    # Calculate assessed total
    calculated_total = sum(
        row["assessed_amount"]
        for row in rows
    )

    # Extract reported total
    match = FINAL_ROW_PATTERN.search(text)

    reported_total = (
        int(match.group(1).replace(",", ""))
        if match else None
    )

    # Validate the table
    serial_numbers = [
        row["serial_number"]
        for row in rows
    ]

    consecutive = serial_numbers == list(
        range(1, len(rows) + 1)
    )

    table_valid = (
        len(rows) > 0
        and reported_total is not None
        and calculated_total == reported_total
        and consecutive
    )

    return {
        "line_items": rows,
        "calculated_total": calculated_total,
        "reported_total": reported_total,
        "table_valid": table_valid
    }


def parse_survey_form(path: str) -> dict:
    reader = PdfReader(path)

    text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    return parse_survey_text(text)


if __name__=="__main__":
    path = "./data/sample_claims/CLM-1006/survey_report.pdf"
    
    output = parse_survey_form(path)

    print(output)