def get_cholesterol_levels() -> dict:
    """Get information about normal cholesterol levels and recommendations."""
    return {
        "total_cholesterol": "Below 200 mg/dL",
        "ldl_bad": {
            "optimal": "Below 100 mg/dL",
            "high_risk": "Below 70 mg/dL or even 55 mg/dL for diabetes/heart disease",
        },
        "hdl_good": {
            "men": "At least 40 mg/dL",
            "women": "At least 50 mg/dL",
            "protective": "60 mg/dL or higher",
        },
        "triglycerides": "Less than 150 mg/dL (fasting)",
    }


def get_cholesterol_doctors() -> dict:
    """Get contact information for doctors who specialize in cholesterol management."""
    return {
        "doctors": [
            {"name": "Dr. Smith", "contact": "123-456-7890"},
            {"name": "Dr. Johnson", "contact": "987-654-3210"},
        ]
    }


def get_cholesterol_medications() -> list:
    """Get list of medications commonly used for cholesterol management."""
    return [
        {"type": "Statins", "examples": ["Atorvastatin", "Simvastatin"]},
        {"type": "Ezetimibe", "examples": ["Zetia"]},
        {"type": "PCSK9 Inhibitors", "examples": ["Alirocumab", "Evolocumab"]},
    ]


def diagnose_cholesterol(
    total: float, ldl: float, hdl: float, triglycerides: float
) -> dict:
    """Diagnose cholesterol levels and provide recommendations."""
    diagnosis = []
    recommendations = []

    if total >= 240:
        diagnosis.append("High total cholesterol")
        recommendations.append("Consider lifestyle changes and medication")
    elif total >= 200:
        diagnosis.append("Borderline high total cholesterol")
        recommendations.append("Focus on diet and exercise")
    else:
        diagnosis.append("Normal total cholesterol")

    if ldl >= 190:
        diagnosis.append("Very high LDL")
        recommendations.append(
            "Immediate medical attention and medication likely needed"
        )
    elif ldl >= 160:
        diagnosis.append("High LDL")
        recommendations.append("Lifestyle changes and possibly medication")
    elif ldl >= 130:
        diagnosis.append("Borderline high LDL")
        recommendations.append("Improve diet and increase physical activity")
    elif ldl < 100:
        diagnosis.append("Optimal LDL")

    if hdl < 40:
        diagnosis.append("Low HDL (increased risk)")
        recommendations.append(
            "Increase physical activity and consider omega-3 supplements"
        )
    elif hdl >= 60:
        diagnosis.append("High HDL (protective)")

    if triglycerides >= 500:
        diagnosis.append("Very high triglycerides")
        recommendations.append("Immediate medical attention needed")
    elif triglycerides >= 200:
        diagnosis.append("High triglycerides")
        recommendations.append("Reduce sugar and refined carbs, increase omega-3")
    elif triglycerides >= 150:
        diagnosis.append("Borderline high triglycerides")
        recommendations.append("Monitor diet and exercise")
    else:
        diagnosis.append("Normal triglycerides")

    return {
        "diagnosis": ", ".join(diagnosis),
        "recommendations": recommendations,
        "values": {
            "total": total,
            "ldl": ldl,
            "hdl": hdl,
            "triglycerides": triglycerides,
        },
    }
