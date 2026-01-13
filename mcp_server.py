"""
MCP Server with FastMCP
This server provides medical information tools for cholesterol and diabetes management.
Uses shared medical_core module for all medical logic.
"""

from fastmcp import FastMCP

from medical_core import (
    calculate_diabetes_risk,
    diagnose_cholesterol,
    get_cholesterol_doctors,
    get_cholesterol_levels,
    get_cholesterol_medications,
    get_diabetes_test_info,
)

mcp = FastMCP("Medical Assistant Server")


@mcp.tool()
def get_cholesterol_levels_mcp() -> dict:
    """Get information about normal cholesterol levels and recommendations.

    Returns:
        dict: Information about cholesterol levels and their normal ranges
    """
    return get_cholesterol_levels()


@mcp.tool()
def get_cholesterol_doctors_mcp() -> dict:
    """Get contact information for doctors who specialize in cholesterol management.

    Returns:
        dict: Doctor names and contact information
    """
    return get_cholesterol_doctors()


@mcp.tool()
def get_cholesterol_medications_mcp() -> list:
    """Get list of medications commonly used for cholesterol management.

    Returns:
        list: List of medication types and examples
    """
    return get_cholesterol_medications()


@mcp.tool()
def get_diabetes_test_info_mcp(test_type: str = "all") -> dict:
    """Get information about diabetes tests and their normal ranges.

    Args:
        test_type: Type of test to get info for. Options: "FPG", "OGTT", "HbA1c", "RPG", or "all"

    Returns:
        dict: Information about diabetes test(s) and their normal ranges
    """
    return get_diabetes_test_info(test_type)


@mcp.tool()
def diagnose_cholesterol_mcp(
    total: float, ldl: float, hdl: float, triglycerides: float
) -> dict:
    """Diagnose cholesterol levels and provide recommendations.

    Args:
        total: Total cholesterol level in mg/dL
        ldl: LDL cholesterol level in mg/dL
        hdl: HDL cholesterol level in mg/dL
        triglycerides: Triglyceride level in mg/dL

    Returns:
        dict: Diagnosis and recommendations
    """
    return diagnose_cholesterol(total, ldl, hdl, triglycerides)


@mcp.tool()
def calculate_diabetes_risk_mcp(
    fpg: float | None = None, hba1c: float | None = None
) -> dict:
    """Calculate diabetes risk based on test results.

    Args:
        fpg: Fasting Plasma Glucose level in mg/dL (optional)
        hba1c: Hemoglobin A1C percentage (optional)

    Returns:
        dict: Risk assessment and recommendations
    """
    return calculate_diabetes_risk(fpg, hba1c)


if __name__ == "__main__":
    mcp.run()
