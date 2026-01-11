import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI()
store = {}


# Medical knowledge functions (duplicated from MCP server logic)
def _get_cholesterol_levels() -> dict:
    """Get information about normal cholesterol levels."""
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


def _get_doctors() -> dict:
    """Get doctor contact information."""
    return {
        "doctors": {
            "cholesterol_specialists": [
            {"name": "Dr. Smith", "contact": "123-456-7890"},
            {"name": "Dr. Johnson", "contact": "987-654-3210"}
        ],
        "diabetes_specialists": [
            {"name": "Dr. Lee", "contact": "555-123-4567"},
            {"name": "Dr. Patel", "contact": "555-987-6543"}
        ]
        }
    }


def _get_cholesterol_medications() -> list:
    """Get cholesterol medications."""
    return [
        {"type": "Statins", "examples": ["Atorvastatin", "Simvastatin"]},
        {"type": "Ezetimibe", "examples": ["Zetia"]},
        {"type": "PCSK9 Inhibitors", "examples": ["Alirocumab", "Evolocumab"]}
    ]


def _get_diabetes_test_info(test_type: str = "all") -> dict:
    """Get diabetes test information."""
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


def _diagnose_cholesterol(total: float, ldl: float, hdl: float, triglycerides: float) -> dict:
    """Diagnose cholesterol levels."""
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
        recommendations.append("Immediate medical attention and medication likely needed")
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
        recommendations.append("Increase physical activity and consider omega-3 supplements")
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
            "triglycerides": triglycerides
        }
    }


def _calculate_diabetes_risk(fpg: float = None, hba1c: float = None) -> dict:
    """Calculate diabetes risk."""
    results = {"tests": {}}
    
    if fpg is not None:
        if fpg >= 126:
            results["tests"]["FPG"] = {
                "value": fpg,
                "status": "Diabetes",
                "recommendation": "Consult healthcare provider immediately"
            }
        elif fpg >= 100:
            results["tests"]["FPG"] = {
                "value": fpg,
                "status": "Prediabetes",
                "recommendation": "Lifestyle changes needed"
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
                "recommendation": "Consult healthcare provider immediately"
            }
        elif hba1c >= 5.7:
            results["tests"]["HbA1c"] = {
                "value": hba1c,
                "status": "Prediabetes",
                "recommendation": "Lifestyle changes needed"
            }
        else:
            results["tests"]["HbA1c"] = {
                "value": hba1c,
                "status": "Normal",
                "recommendation": "Continue healthy lifestyle"
            }
    
    return results


def _get_first_aid_advice(condition: str) -> dict:
    """Get first aid advice for medical conditions."""
    first_aid_guides = {
        "high_cholesterol": {
            "immediate_actions": [
                "Do not panic - high cholesterol is manageable",
                "Schedule appointment with doctor for proper evaluation",
                "Start documenting your diet and exercise habits"
            ],
            "lifestyle_changes": [
                "Reduce saturated fats and trans fats in diet",
                "Increase fiber intake (oats, beans, fruits)",
                "Exercise at least 30 minutes daily",
                "Maintain healthy weight",
                "Quit smoking if applicable"
            ],
            "warning_signs": "Seek immediate medical help if experiencing chest pain, shortness of breath, or severe symptoms"
        },
        "diabetes": {
            "immediate_actions": [
                "Check blood sugar levels if possible",
                "Stay hydrated with water",
                "Contact healthcare provider for guidance"
            ],
            "lifestyle_changes": [
                "Monitor blood sugar regularly",
                "Follow diabetic meal plan",
                "Exercise regularly with doctor approval",
                "Take medications as prescribed"
            ],
            "emergency": "Call emergency services if experiencing severe symptoms like confusion, loss of consciousness, or very high/low blood sugar"
        },
        "general": {
            "immediate_actions": [
                "Stay calm and assess the situation",
                "Contact healthcare provider for advice",
                "Document symptoms and measurements"
            ],
            "when_to_seek_help": [
                "Severe or persistent symptoms",
                "Chest pain or difficulty breathing",
                "Sudden changes in condition",
                "Confusion or loss of consciousness"
            ]
        }
    }
    
    condition_key = condition.lower().replace(" ", "_")
    return first_aid_guides.get(condition_key, first_aid_guides["general"])


# Wrap functions as LangChain tools
@tool
def get_cholesterol_info() -> dict:
    """Get information about normal cholesterol levels and recommendations."""
    return _get_cholesterol_levels()


@tool
def get_doctor_contacts() -> dict:
    """Get contact information for doctors who specialize in cholesterol management."""
    return _get_doctors()


@tool
def get_medications() -> list:
    """Get list of medications commonly used for cholesterol management."""
    return _get_cholesterol_medications()


@tool
def get_diabetes_info(test_type: str = "all") -> dict:
    """Get information about diabetes tests and their normal ranges.
    
    Args:
        test_type: Type of test. Options: FPG, OGTT, HbA1c, RPG, or all
    """
    return _get_diabetes_test_info(test_type)


@tool
def diagnose_cholesterol_levels(total: float, ldl: float, hdl: float, triglycerides: float) -> dict:
    """Diagnose cholesterol levels and provide recommendations.
    
    Args:
        total: Total cholesterol level in mg/dL
        ldl: LDL cholesterol level in mg/dL
        hdl: HDL cholesterol level in mg/dL
        triglycerides: Triglyceride level in mg/dL
    """
    return _diagnose_cholesterol(total, ldl, hdl, triglycerides)


@tool
def assess_diabetes_risk(fpg: float = None, hba1c: float = None) -> dict:
    """Calculate diabetes risk based on test results.
    
    Args:
        fpg: Fasting Plasma Glucose level in mg/dL (optional)
        hba1c: Hemoglobin A1C percentage (optional)
    """
    return _calculate_diabetes_risk(fpg, hba1c)


@tool
def get_first_aid(condition: str) -> dict:
    """Get first aid advice for medical conditions.
    
    Args:
        condition: The medical condition (e.g., 'high_cholesterol', 'diabetes', 'general')
    """
    return _get_first_aid_advice(condition)


def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


class QueryRequest(BaseModel):
    query: str
    model: str = "z-ai/glm-4.5-air:free"
    session_id: str = "default"


class QueryResponse(BaseModel):
    diagnosis: Optional[str] = None
    recomendation: Optional[str] = None
    description: Optional[str] = None
    medications: Optional[str] = None
    first_aid: Optional[str] = None
    doctor_contact: Optional[str] = None
    model: str
    session_id: str


@app.get("/")
async def root():
    return {
        "message": "FastAPI LangChain Server with MCP Tools",
        "mcp_tools": [
            "get_cholesterol_info",
            "get_doctor_contacts", 
            "get_medications",
            "get_diabetes_info",
            "diagnose_cholesterol_levels",
            "assess_diabetes_risk",
            "get_first_aid"
        ]
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")

    # Initialize LLM
    llm = ChatOpenAI(
        model=request.model,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.3,  # Lower temperature for more consistent output
        max_tokens=1080
    )

    # Get conversation history
    session_history = get_session_history(request.session_id)
    
    # Define tools from MCP server
    tools = [
        get_cholesterol_info,
        get_doctor_contacts,
        get_medications,
        get_diabetes_info,
        diagnose_cholesterol_levels,
        assess_diabetes_risk,
        get_first_aid,
    ]

    # Create system prompt with strong JSON emphasis
    system_prompt = """You are a medical assistant API that MUST return valid JSON.

After using any tools, you MUST format your final response as valid JSON with this EXACT structure:
{
  "diagnosis": "string or null",
  "recomendation": "string or null",
  "description": "string describing findings",
  "medications": "string or null",
  "first_aid": "string or null",
  "doctor_contact": "string or null"
}

Rules:
1. ALWAYS use tools when relevant data is requested
2. After gathering information from tools, synthesize it into the JSON format above
3. Return ONLY the JSON object, no markdown, no explanation, no extra text
4. Use null for fields that don't apply
5. Use get_doctor_contacts tool when doctor information is needed and include in doctor_contact field
6. Use get_first_aid tool when first aid advice is requested and include in first_aid field
7. Keep responses professional and concise

Example valid response:
{
  "diagnosis": "Borderline high cholesterol",
  "recomendation": "Increase exercise and improve diet",
  "description": "Total cholesterol of 220 mg/dL is above the normal range of 200 mg/dL",
  "medications": "Consider statins if lifestyle changes are insufficient",
  "first_aid": "Start by reducing saturated fats and exercising 30 minutes daily",
  "doctor_contact": "Dr. Smith: 123-456-7890, Dr. Johnson: 987-654-3210"
}"""


    # Create agent with MCP tools
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )

    try:
        # Prepare messages with history
        history_messages = []
        for msg in session_history.messages:
            if msg.type == "human":
                history_messages.append(("user", msg.content))
            elif msg.type == "ai":
                history_messages.append(("assistant", msg.content))
        
        # Add current query
        current_messages = history_messages + [("user", request.query)]
        
        # Invoke agent (synchronous call)
        response = agent.invoke({
            "messages": current_messages,
        })
        
        # Get final response
        final_message = response["messages"][-1].content

        
        # Clean the response (remove markdown code blocks if present)
        cleaned_message = final_message.strip()
        if cleaned_message.startswith("```json"):
            cleaned_message = cleaned_message[7:]
        elif cleaned_message.startswith("```"):
            cleaned_message = cleaned_message[3:]
        if cleaned_message.endswith("```"):
            cleaned_message = cleaned_message[:-3]
        cleaned_message = cleaned_message.strip()
        
        # Add to session history
        session_history.add_user_message(request.query)
        session_history.add_ai_message(cleaned_message)
        
        # Parse JSON response
        try:
            response_data = json.loads(cleaned_message)
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract JSON from the text
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned_message)
            if json_match:
                try:
                    response_data = json.loads(json_match.group(0))
                except:
                    # Last resort: create a response with the raw text
                    response_data = {
                        "diagnosis": None,
                        "recomendation": None,
                        "description": cleaned_message,
                        "medications": None,
                        "first_aid": None,
                        "doctor_contact": None
                    }
            else:
                # No JSON found, use raw text as description
                response_data = {
                    "diagnosis": None,
                    "recomendation": None,
                    "description": cleaned_message,
                    "medications": None,
                    "first_aid": None,
                    "doctor_contact": None
                }
        
        return QueryResponse(
            diagnosis=response_data.get("diagnosis"),
            recomendation=response_data.get("recomendation"),
            description=response_data.get("description"),
            medications=response_data.get("medications"),
            first_aid=response_data.get("first_aid"),
            doctor_contact=response_data.get("doctor_contact"),
            model=request.model,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
