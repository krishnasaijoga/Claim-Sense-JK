import re


def find_labels(text:str,LABEL_PATTERNS:dict)->list[dict]:
    matches=[]

    for field, pattern in LABEL_PATTERNS.items():
        anchored = rf"^[ \t]*({pattern})"
        for match in re.finditer(
            anchored,
            text,
            flags=re.IGNORECASE|re.MULTILINE
        ):
            matches.append({
                "field": field,
                "start": match.start(),
                "end": match.end(),
            })
    return sorted(matches, key=lambda item: item["start"])