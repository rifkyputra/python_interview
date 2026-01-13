import logging
import os
from typing import Literal, TypedDict, cast

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
import time

from medical_core import (
    calculate_diabetes_risk,
    diagnose_cholesterol,
    get_cholesterol_doctors,
    get_cholesterol_levels,
    get_cholesterol_medications,
    get_diabetes_test_info,
    get_first_aid_advice,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalState(TypedDict):
    messages: list[BaseMessage]
    query: str
    query_type: Literal["cholesterol", "diabetes", "general", "unknown"] | None
    has_lab_values: bool
    risk_level: Literal["low", "moderate", "high", "critical"] | None
    needs_doctor: bool
    needs_first_aid: bool
    cholesterol_values: dict | None
    diabetes_values: dict | None
    final_response: str


def classify_query(state: MedicalState) -> MedicalState:
    """Classify the query type based on content."""
    query = state["query"].lower()

    query_type: Literal["cholesterol", "diabetes", "general", "unknown"] = "unknown"
    has_lab_values = False

    cholesterol_keywords = [
        "cholesterol",
        "ldl",
        "hdl",
        "triglycerides",
        "total cholesterol",
    ]
    diabetes_keywords = [
        "diabetes",
        "glucose",
        "blood sugar",
        "hba1c",
        "a1c",
        "prediabetes",
    ]

    if any(kw in query for kw in diabetes_keywords):
        query_type = "diabetes"
    elif any(kw in query for kw in cholesterol_keywords):
        query_type = "cholesterol"
    elif "?" in query or "help" in query or "advice" in query:
        query_type = "general"

    import re

    if re.search(r"\d+\s*(?:mg/dl|%)", query):
        if re.search(r"\b(?:100|126|200|140|5\.7|6\.5)\b", query):
            has_lab_values = True

    return cast(
        MedicalState,
        {
            **state,
            "query_type": query_type,
            "has_lab_values": has_lab_values,
        },
    )


def route_by_query_type(
    state: MedicalState,
) -> Literal["cholesterol_flow", "diabetes_flow", "general_flow"]:
    """Route to appropriate flow based on query type."""
    query_type = state["query_type"] or "general"
    routes: dict[str, Literal["cholesterol_flow", "diabetes_flow", "general_flow"]] = {
        "cholesterol": "cholesterol_flow",
        "diabetes": "diabetes_flow",
        "general": "general_flow",
        "unknown": "general_flow",
    }
    return routes.get(query_type, "general_flow")


def extract_cholesterol_values(state: MedicalState) -> MedicalState:
    """Extract cholesterol lab values from query if present."""
    query = state["query"]
    import re

    values: dict[str, float] = {}

    total_match = re.search(r"total[:\s]*(\d+(?:\.\d+)?)", query)
    if total_match:
        values["total"] = float(total_match.group(1))

    ldl_match = re.search(r"(?:ldl|bad)[:\s]*(\d+(?:\.\d+)?)", query)
    if ldl_match:
        values["ldl"] = float(ldl_match.group(1))

    hdl_match = re.search(r"(?:hdl|good)[:\s]*(\d+(?:\.\d+)?)", query)
    if hdl_match:
        values["hdl"] = float(hdl_match.group(1))

    tg_match = re.search(r"(?:triglycerides?|tg)[:\s]*(\d+(?:\.\d+)?)", query)
    if tg_match:
        values["triglycerides"] = float(tg_match.group(1))

    has_all = all(k in values for k in ["total", "ldl", "hdl", "triglycerides"])

    return cast(
        MedicalState,
        {
            **state,
            "cholesterol_values": values if values else None,
            "has_lab_values": has_all or state["has_lab_values"],
        },
    )


def assess_cholesterol_risk(state: MedicalState) -> MedicalState:
    """Assess cholesterol risk level."""
    values = state.get("cholesterol_values")

    if not values:
        return cast(
            MedicalState,
            {**state, "risk_level": None},
        )

    risk: Literal["low", "moderate", "high", "critical"] = "low"

    if values.get("total", 0) >= 240 or values.get("ldl", 0) >= 190:
        risk = "critical"
    elif values.get("total", 0) >= 200 or values.get("ldl", 0) >= 160:
        risk = "high"
    elif values.get("total", 0) >= 180 or values.get("ldl", 0) >= 130:
        risk = "moderate"

    return cast(MedicalState, {**state, "risk_level": risk})


def route_cholesterol_flow(
    state: MedicalState,
) -> Literal["diagnose_cholesterol", "get_cholesterol_info"]:
    """Route based on whether lab values are present."""
    return (
        "diagnose_cholesterol"
        if state.get("cholesterol_values")
        else "get_cholesterol_info"
    )


def get_cholesterol_info_node(state: MedicalState) -> MedicalState:
    """Get general cholesterol information."""
    info = get_cholesterol_levels()
    meds = get_cholesterol_medications()
    doctors = get_cholesterol_doctors()

    return cast(
        MedicalState,
        {
            **state,
            "final_response": f"Cholesterol Information:\n\nLevels: {info}\n\nMedications: {meds}\n\nDoctors: {doctors}",
        },
    )


def diagnose_cholesterol_node(state: MedicalState) -> MedicalState:
    """Diagnose cholesterol with provided values."""
    values = state.get("cholesterol_values", {})

    if not values:
        return cast(
            MedicalState,
            {
                **state,
                "final_response": "No cholesterol values provided for diagnosis.",
            },
        )

    result = diagnose_cholesterol(
        total=values.get("total", 0),
        ldl=values.get("ldl", 0),
        hdl=values.get("hdl", 0),
        triglycerides=values.get("triglycerides", 0),
    )

    risk = state.get("risk_level", "moderate")
    needs_doctor = risk in ["high", "critical"]

    response = f"Diagnosis: {result['diagnosis']}\n\nRecommendations: {result['recommendations']}\n\nValues: {result['values']}\n\nRisk Level: {risk}"

    if needs_doctor:
        doctors = get_cholesterol_doctors()
        response += f"\n\nPlease consult a specialist: {doctors['doctors']}"

    return cast(
        MedicalState,
        {
            **state,
            "final_response": response,
            "risk_level": risk,
            "needs_doctor": needs_doctor,
        },
    )


def extract_diabetes_values(state: MedicalState) -> MedicalState:
    """Extract diabetes lab values from query if present."""
    query = state["query"]
    import re

    values: dict[str, float] = {}

    fpg_match = re.search(r"(?:fpg|fasting|glucose)[:\s]*(\d+(?:\.\d+)?)", query)
    if fpg_match:
        values["fpg"] = float(fpg_match.group(1))

    hba1c_match = re.search(r"(?:hba1c|a1c)[:\s]*(\d+(?:\.\d+)?)", query)
    if hba1c_match:
        values["hba1c"] = float(hba1c_match.group(1))

    has_any = len(values) > 0

    return cast(
        MedicalState,
        {
            **state,
            "diabetes_values": values if values else None,
            "has_lab_values": has_any or state["has_lab_values"],
        },
    )


def assess_diabetes_risk(state: MedicalState) -> MedicalState:
    """Assess diabetes risk level."""
    values = state.get("diabetes_values", {})

    if not values:
        return cast(
            MedicalState,
            {**state, "risk_level": None},
        )

    risk: Literal["low", "moderate", "high", "critical"] = "low"

    fpg = values.get("fpg", 0)
    hba1c = values.get("hba1c", 0)

    if fpg >= 126 or hba1c >= 6.5:
        risk = "critical"
    elif fpg >= 100 or hba1c >= 5.7:
        risk = "high"
    elif fpg >= 90 or hba1c >= 5.5:
        risk = "moderate"

    return cast(MedicalState, {**state, "risk_level": risk})


def route_diabetes_flow(
    state: MedicalState,
) -> Literal["diagnose_diabetes", "get_diabetes_info"]:
    """Route based on whether lab values are present."""
    return "diagnose_diabetes" if state.get("diabetes_values") else "get_diabetes_info"


def get_diabetes_info_node(state: MedicalState) -> MedicalState:
    """Get general diabetes information."""
    info = get_diabetes_test_info("all")

    return cast(
        MedicalState,
        {
            **state,
            "final_response": f"Diabetes Test Information:\n\n{info}",
        },
    )


def diagnose_diabetes_node(state: MedicalState) -> MedicalState:
    """Diagnose diabetes with provided values."""
    values = state.get("diabetes_values", {})

    if not values:
        return cast(
            MedicalState,
            {
                **state,
                "final_response": "No diabetes values provided for diagnosis.",
            },
        )

    result = calculate_diabetes_risk(
        fpg=values.get("fpg"),
        hba1c=values.get("hba1c"),
    )

    risk = state.get("risk_level", "moderate")
    needs_doctor = risk in ["high", "critical"]

    response = f"Diabetes Risk Assessment:\n\n{result}\n\nRisk Level: {risk}"

    if needs_doctor:
        response += (
            "\n\nPlease consult a healthcare provider for confirmation and treatment."
        )

    return cast(
        MedicalState,
        {
            **state,
            "final_response": response,
            "risk_level": risk,
            "needs_doctor": needs_doctor,
        },
    )


def general_flow_node(state: MedicalState) -> MedicalState:
    """Handle general queries."""
    api_key = os.getenv("OPENROUTER_API_KEY")

    llm = ChatOpenAI(
        model="google/gemini-3-flash-preview",  # type: ignore
        api_key=api_key,  # type: ignore
        base_url="https://openrouter.ai/api/v1",  # type: ignore
        temperature=0.3,
        timeout=6,
    )

    logger.info("Invoking LLM for general query: %s", state["query"])
    start = time.time()

    response = llm.invoke(
        [
            HumanMessage(
                content=f"You are a medical assistant. Provide helpful, general guidance for this query: {state['query']}. never return markdown formatting. skip greetings, goodbyes, or disclaimers. skip follow-up questions."
            )
        ]
    )

    final_response = response.content if hasattr(response, "content") else str(response)
    end = time.time()
    logger.info(f"LLM response time: {end - start:.2f} seconds")
    return cast(
        MedicalState,
        {**state, "final_response": final_response},
    )


def check_emergency(state: MedicalState) -> Literal["first_aid", "format_response"]:
    """Check if emergency response is needed."""
    if state.get("risk_level") in ["critical", "high"]:
        return "first_aid"
    return "format_response"


def first_aid_node(state: MedicalState) -> MedicalState:
    """Provide first aid advice for high-risk cases."""
    query = state["query"]
    condition = "general"

    if "cholesterol" in query.lower():
        condition = "high_cholesterol"
    elif "diabetes" in query.lower() or "glucose" in query.lower():
        condition = "diabetes"

    advice = get_first_aid_advice(condition)

    response = (
        "IMPORTANT: Based on your risk level, please take the following steps:\n\n"
    )
    response += f"Immediate Actions: {advice['immediate_actions']}\n\n"
    response += f"Lifestyle Changes: {advice['lifestyle_changes']}\n\n"

    if "warning_signs" in advice:
        response += f"Warning Signs: {advice['warning_signs']}\n\n"
    if "emergency" in advice:
        response += f"Emergency: {advice['emergency']}\n\n"

    return cast(
        MedicalState,
        {**state, "final_response": response, "needs_first_aid": True},
    )


def format_response(state: MedicalState) -> MedicalState:
    """Format the final response."""
    return cast(
        MedicalState,
        {
            **state,
            "final_response": state.get("final_response", "No response generated."),
        },
    )


def create_medical_graph():
    """Create the LangGraph state machine for medical queries."""

    graph = StateGraph(MedicalState)  # type: ignore

    graph.set_entry_point("classify_query")

    graph.add_node("classify_query", classify_query)
    graph.add_node("extract_cholesterol_values", extract_cholesterol_values)
    graph.add_node("assess_cholesterol_risk", assess_cholesterol_risk)
    graph.add_node("get_cholesterol_info_node", get_cholesterol_info_node)
    graph.add_node("diagnose_cholesterol_node", diagnose_cholesterol_node)
    graph.add_node("extract_diabetes_values", extract_diabetes_values)
    graph.add_node("assess_diabetes_risk", assess_diabetes_risk)
    graph.add_node("get_diabetes_info_node", get_diabetes_info_node)
    graph.add_node("diagnose_diabetes_node", diagnose_diabetes_node)
    graph.add_node("general_flow_node", general_flow_node)
    graph.add_node("first_aid_node", first_aid_node)
    graph.add_node("format_response", format_response)

    graph.add_conditional_edges(
        "classify_query",
        route_by_query_type,
        {
            "cholesterol_flow": "extract_cholesterol_values",
            "diabetes_flow": "extract_diabetes_values",
            "general_flow": "general_flow_node",
            "unknown": "general_flow_node",
        },
    )

    graph.add_edge("extract_cholesterol_values", "assess_cholesterol_risk")

    graph.add_conditional_edges(
        "assess_cholesterol_risk",
        route_cholesterol_flow,
        {
            "diagnose_cholesterol": "diagnose_cholesterol_node",
            "get_cholesterol_info": "get_cholesterol_info_node",
        },
    )

    graph.add_edge("extract_diabetes_values", "assess_diabetes_risk")

    graph.add_conditional_edges(
        "assess_diabetes_risk",
        route_diabetes_flow,
        {
            "diagnose_diabetes": "diagnose_diabetes_node",
            "get_diabetes_info": "get_diabetes_info_node",
        },
    )

    graph.add_conditional_edges(
        "general_flow_node",
        check_emergency,
        {
            "first_aid": "first_aid_node",
            "format_response": "format_response",
        },
    )

    graph.add_conditional_edges(
        "diagnose_cholesterol_node",
        check_emergency,
        {
            "first_aid": "first_aid_node",
            "format_response": "format_response",
        },
    )

    graph.add_conditional_edges(
        "diagnose_diabetes_node",
        check_emergency,
        {
            "first_aid": "first_aid_node",
            "format_response": "format_response",
        },
    )

    graph.add_edge("get_cholesterol_info_node", "format_response")
    graph.add_edge("get_diabetes_info_node", "format_response")
    graph.add_edge("first_aid_node", "format_response")
    graph.add_edge("format_response", END)

    return graph.compile()


medical_graph = create_medical_graph()


def run_medical_graph(query: str) -> str:
    """Run the medical graph with a query."""
    initial_state: MedicalState = {
        "messages": [HumanMessage(content=query)],
        "query": query,
        "query_type": None,
        "has_lab_values": False,
        "risk_level": None,
        "needs_doctor": False,
        "needs_first_aid": False,
        "cholesterol_values": None,
        "diabetes_values": None,
        "final_response": "",
    }

    result = medical_graph.invoke(initial_state)
    return result["final_response"]


async def run_medical_graph_streaming(query: str):
    """Run the medical graph with streaming for WebSocket."""
    import asyncio

    initial_state: MedicalState = {
        "messages": [HumanMessage(content=query)],
        "query": query,
        "query_type": None,
        "has_lab_values": False,
        "risk_level": None,
        "needs_doctor": False,
        "needs_first_aid": False,
        "cholesterol_values": None,
        "diabetes_values": None,
        "final_response": "",
    }

    try:
        # Use astream to get streaming updates from LangGraph
        async for event in medical_graph.astream(initial_state):
            for node_name, state in event.items():
                # Yield progress updates for each node execution
                yield f"Processing: {node_name}..."

                # For the general_flow_node, we can potentially stream LLM tokens
                if node_name == "general_flow_node" and state.get("final_response"):
                    # Stream the final response character by character for effect
                    response = state.get("final_response", "")
                    for i in range(
                        0, len(response), 50
                    ):  # Stream in chunks of 50 chars
                        chunk = response[i : i + 50]
                        yield chunk
                        await asyncio.sleep(0.01)  # Small delay for streaming effect

        # After streaming is complete, yield the final result
        result = medical_graph.invoke(initial_state)
        final_response = result["final_response"]

        # If we didn't stream the final response above, yield it now
        if final_response:
            yield final_response

    except Exception as e:
        yield f"Error: {str(e)}"
