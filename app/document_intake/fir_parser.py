from pathlib import Path
from pypdf import PdfReader

from app.document_intake.label_parser import find_labels

LABEL_PATTERNS={
    "fir_number":r"FIR\s+number",
    "police_station":r"Police\s+station",
    "date_of_incident":r"Date\s+of\s+incident",
    "time_of_incident":r"Time\s+of\s+incident",
    "place_of_incident":r"Place\s+of\s+incident",
    "vehicle_involved":r"Vehicle\s+involved",
    "breath_analyser_result":(
        r"Breath\s+analyser\s+result\s*"
        r"\(driver\s+of\s+insured\s+vehicle\)"
    ),
    "brief_facts":r"Brief\s+facts"
}

REQUIRED_FIR_FIELDS = {
    "fir_number",
    "date_of_incident",
    "vehicle_involved",
    "breath_analyser_result",
    "brief_facts",
}


def get_fir_status(data: dict) -> str:
    missing_fields = [
        field
        for field in REQUIRED_FIR_FIELDS
        if data.get(field) is None
    ]

    return "PARTIAL" if missing_fields else "SUCCESS"


def parse_fir_fields(text:str)->dict:
    labels=find_labels(text,LABEL_PATTERNS)

    result={field:None for field in LABEL_PATTERNS}

    for i, current in enumerate(labels):
        field=current["field"]

        if field not in result:
            continue

        start=current["end"]

        if i+1<len(labels):
            end=labels[i+1]["start"]
        else:
            end=len(text)

        value=" ".join(text[start:end].split())

        if value:
            result[field]=value # type: ignore
    return result


def parse_fir_form(path:str)->dict:
    file_path=Path(path)

    if not file_path.is_file():
        return {
            "fir_status":"NOT_PROVIDED"
        }
    try:
        reader = PdfReader(path)
        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

        extracted_fields = parse_fir_fields(text)

        fir_status=get_fir_status(extracted_fields)

        return {
            **extracted_fields,
            "fir_status":fir_status
        }
    except Exception as exc:
        return {
            "fir_status": "FAILED",
            "error": str(exc)
        }


if __name__=="__main__":
    path = "./data/sample_claims/CLM-1001/fir.pdf"
    
    output = parse_fir_form(path)

    for key, value in output.items():
        print(f"{key}: {value}")