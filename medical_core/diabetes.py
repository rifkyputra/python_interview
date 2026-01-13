def get_diabetes_test_info(test_type: str = "all") -> dict:
    """Get information about diabetes tests and their normal ranges."""
    tests = {
        "FPG": {
            "name": "Fasting Plasma Glucose",
            "description": "Measures blood sugar after overnight fast (8+ hours)",
            "normal": "Below 100 mg/dL",
            "prediabetes": "100 to 125 mg/dL",
            "diabetes": "126 mg/dL or higher (on two separate tests)",
        },
        "OGTT": {
            "name": "Oral Glucose Tolerance Test",
            "description": "Fast overnight, drink sugary liquid, test after 2 hours",
            "normal": "Below 140 mg/dL",
            "prediabetes": "140 to 199 mg/dL",
            "diabetes": "200 mg/dL or higher",
        },
        "HbA1c": {
            "name": "Hemoglobin A1C",
            "description": "Reflects average blood sugar over past 2-3 months, no fasting required",
            "normal": "Below 5.7%",
            "prediabetes": "5.7% to 6.4%",
            "diabetes": "6.5% or higher (on two separate tests)",
        },
        "RPG": {
            "name": "Random Plasma Glucose",
            "description": "Blood test taken at any time, used if severe symptoms present",
            "diabetes": "200 mg/dL or higher with symptoms",
        },
    }

    if test_type.upper() in tests:
        return {test_type.upper(): tests[test_type.upper()]}
    return tests


def calculate_diabetes_risk(
    fpg: float | None = None, hba1c: float | None = None
) -> dict:
    """Calculate diabetes risk based on test results."""
    results = {"tests": {}}

    if fpg is not None:
        if fpg >= 126:
            results["tests"]["FPG"] = {
                "value": fpg,
                "status": "Diabetes",
                "recommendation": "Consult healthcare provider immediately",
            }
        elif fpg >= 100:
            results["tests"]["FPG"] = {
                "value": fpg,
                "status": "Prediabetes",
                "recommendation": "Lifestyle changes needed",
            }
        else:
            results["tests"]["FPG"] = {
                "value": fpg,
                "status": "Normal",
                "recommendation": "Continue healthy lifestyle",
            }

    if hba1c is not None:
        if hba1c >= 6.5:
            results["tests"]["HbA1c"] = {
                "value": hba1c,
                "status": "Diabetes",
                "recommendation": "Consult healthcare provider immediately",
            }
        elif hba1c >= 5.7:
            results["tests"]["HbA1c"] = {
                "value": hba1c,
                "status": "Prediabetes",
                "recommendation": "Lifestyle changes needed",
            }
        else:
            results["tests"]["HbA1c"] = {
                "value": hba1c,
                "status": "Normal",
                "recommendation": "Continue healthy lifestyle",
            }

    return results
