import json
from pypdf import PdfReader


reader=PdfReader("./data/sample_claims/CLM-1006/claim_form.pdf")

pdf_data={
    "file_name":"claim_form.pdf",
    "total_pages":len(reader.pages),
    "pages":[]
}

for page_number, page in enumerate(reader.pages,start=1):
    pdf_data["pages"].append({
        "page":page_number,
        "text":page.extract_text()
    })

json_output=json.dumps(pdf_data,indent=4)
print(json_output)
