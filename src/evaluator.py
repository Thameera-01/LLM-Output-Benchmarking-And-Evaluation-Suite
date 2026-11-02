import json
import re

def evaluate_llm_response(raw_text: str, test_case: dict) -> dict:
    clean_text = re.sub(r"^```json\s*|^```\s*|```$", "", raw_text.strip(), flags=re.MULTILINE)

    json_valid = False
    parsed_json = {}
    try:
        parsed_json = json.loads(clean_text)
        json_valid = True
    except Exception:
        json_valid = False

    required_terms = test_case.get("required_terms", [])
    matched = [term for term in required_terms if term.lower() in raw_text.lower()]
    term_coverage = round(len(matched) / len(required_terms), 2) if required_terms else 1.0

    expected_sev = test_case.get("expected_severity", "").upper()
    actual_sev = str(parsed_json.get("risk_severity", "")).upper()
    severity_match = (actual_sev == expected_sev) if json_valid else False

    return {
        "valid_json": json_valid,
        "term_coverage": term_coverage,
        "severity_assertion_pass": severity_match
    }