"""
MCP Server with FastMCP
This server provides medical information tools for cholesterol and diabetes management.
"""
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Medical Assistant Server")


@mcp.tool()
def get_cholesterol_levels() -> dict:
    """Get information about normal cholesterol levels and recommendations.
    
    Returns:
        dict: Information about cholesterol levels and their normal ranges
    """
    return {
        "total_cholesterol": "Below 200 mg/dL",
        "ldl_bad": {
            "optimal": "Below 100 mg/dL",
            "high_risk": "Below 70 mg/dL or even 55 mg/dL for diabetes/heart disease"
        },
        "hdl_good": {
            "men": "At least 40 mg/dL",
            "women": "At least 50 mg/dL",
            "protective": "60 mg/dL or higher"
        },
        "triglycerides": "Less than 150 mg/dL (fasting)"
    }


@mcp.tool()
def get_cholesterol_doctors() -> dict:
    """Get contact information for doctors who specialize in cholesterol management.
    
    Returns:
        dict: Doctor names and contact information
    """
    return {
        "doctors": [
            {"name": "Dr. Smith", "contact": "123-456-7890"},
            {"name": "Dr. Johnson", "contact": "987-654-3210"}
        ]
    }


@mcp.tool()
def get_cholesterol_medications() -> list:
    """Get list of medications commonly used for cholesterol management.
    
    Returns:
        list: List of medication types and examples
    """
    return [
        {"type": "Statins", "examples": ["Atorvastatin", "Simvastatin"]},
        {"type": "Ezetimibe", "examples": ["Zetia"]},
        {"type": "PCSK9 Inhibitors", "examples": ["Alirocumab", "Evolocumab"]}
    ]


@mcp.tool()
def get_diabetes_test_info(test_type: str = "all") -> dict:
    """Get information about diabetes tests and their normal ranges.
    
    Args:
        test_type: Type of test to get info for. Options: "FPG", "OGTT", "HbA1c", "RPG", or "all"
    
    Returns:
        dict: Information about diabetes test(s) and their normal ranges
    """
    tests = {
        "FPG": {
            "name": "Fasting Plasma Glucose",
            "description": "Measures blood sugar after overnight fast (8+ hours)",
            "normal": "Below 100 mg/dL",
            "prediabetes": "100 to 125 mg/dL",
            "diabetes": "126 mg/dL or higher (on two separate tests)"
        },
        "OGTT": {
            "name": "Oral Glucose Tolerance Test",
            "description": "Fast overnight, drink sugary liquid, test after 2 hours",
            "normal": "Below 140 mg/dL",
            "prediabetes": "140 to 199 mg/dL",
            "diabetes": "200 mg/dL or higher"
        },
        "HbA1c": {
            "name": "Hemoglobin A1C",
            "description": "Reflects average blood sugar over past 2-3 months, no fasting required",
            "normal": "Below 5.7%",
            "prediabetes": "5.7% to 6.4%",
            "diabetes": "6.5% or higher (on two separate tests)"
        },
        "RPG": {
            "name": "Random Plasma Glucose",
            "description": "Blood test taken at any time, used if severe symptoms present",
            "diabetes": "200 mg/dL or higher with symptoms"
        }
    }
    
    if test_type.upper() in tests:
        return {test_type.upper(): tests[test_type.upper()]}
    return tests


@mcp.tool()
def diagnose_cholesterol(total: float, ldl: float, hdl: float, triglycerides: float) -> dict:
    """Diagnose cholesterol levels and provide recommendations.
    
    Args:
        total: Total cholesterol level in mg/dL
        ldl: LDL cholesterol level in mg/dL
        hdl: HDL cholesterol level in mg/dL
        triglycerides: Triglyceride level in mg/dL
    
    Returns:
        dict: Diagnosis and recommendations
    """
    diagnosis = []
    recommendations = []
    
    # Check total cholesterol
    if total >= 240:
        diagnosis.append("High total cholesterol")
        recommendations.append("Consider lifestyle changes and medication")
    elif total >= 200:
        diagnosis.append("Borderline high total cholesterol")
        recommendations.append("Focus on diet and exercise")
    else:
        diagnosis.append("Normal total cholesterol")
    
    # Check LDL
    if ldl >= 190:
        diagnosis.append("Very high LDL")
        recommendations.append("Immediate medical attention and medication likely needed")
    elif ldl >= 160:
        diagnosis.append("High LDL")
        recommendations.append("Lifestyle changes and possibly medication")
    elif ldl >= 130:
        diagnosis.append("Borderline high LDL")
        recommendations.append("Improve diet and increase physical activity")
    elif ldl < 100:
        diagnosis.append("Optimal LDL")
    
    # Check HDL
    if hdl < 40:
        diagnosis.append("Low HDL (increased risk)")
        recommendations.append("Increase physical activity and consider omega-3 supplements")
    elif hdl >= 60:
        diagnosis.append("High HDL (protective)")
    
    # Check triglycerides
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
            "triglycerides": triglycerides
        }
    }


@mcp.tool()
def calculate_diabetes_risk(fpg: float = None, hba1c: float = None) -> dict:
    """Calculate diabetes risk based on test results.
    
    Args:
        fpg: Fasting Plasma Glucose level in mg/dL (optional)
        hba1c: Hemoglobin A1C percentage (optional)
    
    Returns:
        dict: Risk assessment and recommendations
    """
    results = {"tests": {}}
    
    if fpg is not None:
        if fpg >= 126:
            results["tests"]["FPG"] = {
                "value": fpg,
                "status": "Diabetes",
                "recommendation": "Consult healthcare provider immediately for diagnosis confirmation"
            }
        elif fpg >= 100:
            results["tests"]["FPG"] = {
                "value": fpg,
                "status": "Prediabetes",
                "recommendation": "Lifestyle changes needed to prevent diabetes"
            }
        else:
            results["tests"]["FPG"] = {
                "value": fpg,
                "status": "Normal",
                "recommendation": "Continue healthy lifestyle"
            }
    
    if hba1c is not None:
        if hba1c >= 6.5:
            results["tests"]["HbA1c"] = {
                "value": hba1c,
                "status": "Diabetes",
                "recommendation": "Consult healthcare provider immediately for diagnosis confirmation"
            }
        elif hba1c >= 5.7:
            results["tests"]["HbA1c"] = {
                "value": hba1c,
                "status": "Prediabetes",
                "recommendation": "Lifestyle changes needed to prevent diabetes"
            }
        else:
            results["tests"]["HbA1c"] = {
                "value": hba1c,
                "status": "Normal",
                "recommendation": "Continue healthy lifestyle"
            }
    
    if not results["tests"]:
        return {"error": "Please provide at least one test value (fpg or hba1c)"}
    
    return results


@mcp.resource("medical://guidelines/cholesterol")
def cholesterol_guidelines() -> str:
    """Comprehensive cholesterol management guidelines.
    
    Returns:
        str: Full text of cholesterol guidelines
    """
    return """
    CHOLESTEROL MANAGEMENT GUIDELINES
    
    Target Levels:
    - Total Cholesterol: Below 200 mg/dL
    - LDL (Bad): Below 100 mg/dL (optimal)
    - HDL (Good): Above 40 mg/dL (men), Above 50 mg/dL (women)
    - Triglycerides: Below 150 mg/dL
    
    Lifestyle Modifications:
    1. Diet: Reduce saturated fats, increase fiber
    2. Exercise: At least 150 minutes moderate activity per week
    3. Weight: Achieve and maintain healthy body weight
    4. Smoking: Quit smoking
    
    When to Consider Medication:
    - LDL > 190 mg/dL
    - Diabetes and LDL > 70 mg/dL
    - High cardiovascular risk
    
    Available Medications:
    - Statins (first-line therapy)
    - Ezetimibe (cholesterol absorption inhibitor)
    - PCSK9 inhibitors (for high-risk patients)
    """


@mcp.resource("medical://guidelines/diabetes")
def diabetes_guidelines() -> str:
    """Comprehensive diabetes testing and management guidelines.
    
    Returns:
        str: Full text of diabetes guidelines
    """
    return """
    DIABETES TESTING & MANAGEMENT GUIDELINES
    
    Diagnostic Tests:
    1. Fasting Plasma Glucose (FPG): 8+ hours fasting
       - Normal: <100 mg/dL
       - Prediabetes: 100-125 mg/dL
       - Diabetes: ≥126 mg/dL
    
    2. Hemoglobin A1C (HbA1c): No fasting required
       - Normal: <5.7%
       - Prediabetes: 5.7-6.4%
       - Diabetes: ≥6.5%
    
    3. Oral Glucose Tolerance Test (OGTT): 2-hour test
       - Normal: <140 mg/dL
       - Prediabetes: 140-199 mg/dL
       - Diabetes: ≥200 mg/dL
    
    Prevention & Management:
    1. Diet: Low glycemic index foods, portion control
    2. Exercise: Regular physical activity
    3. Weight management: Lose 5-7% body weight if overweight
    4. Monitor blood sugar regularly
    5. Take medications as prescribed
    """


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
