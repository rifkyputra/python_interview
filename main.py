import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langgraph_app import run_medical_graph

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = {}


class QueryRequest(BaseModel):
    query: str
    model: str = "google/gemini-3-flash-preview"
    session_id: str = "default"


class QueryResponse(BaseModel):
    diagnosis: str | None = None
    recomendation: str | None = None
    description: str | None = None
    medications: str | None = None
    first_aid: str | None = None
    doctor_contact: str | None = None
    model: str
    session_id: str


@app.get("/")
async def root():
    return {
        "message": "FastAPI LangGraph Server with Medical Core",
        "mode": "langgraph",
        "query_types": ["cholesterol", "diabetes", "general"],
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")

    try:
        response_text = run_medical_graph(request.query)
        response = parse_response(response_text)
        response["model"] = request.model
        response["session_id"] = request.session_id
        return QueryResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from None


@app.websocket("/ws/query")
async def websocket_query(websocket: WebSocket):
    """WebSocket endpoint for streaming medical AI responses."""
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            query = data.get("query", "")
            model = data.get("model", "google/gemini-3-flash-preview")
            session_id = data.get("session_id", "default")

            if not query:
                await websocket.send_json(
                    {"type": "error", "data": "Query is required"}
                )
                continue

            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                await websocket.send_json(
                    {"type": "error", "data": "OPENROUTER_API_KEY not configured"}
                )
                continue

            # Send status update
            await websocket.send_json(
                {"type": "status", "data": "Processing your medical query..."}
            )

            try:
                # Import here to avoid circular imports
                from langgraph_app import run_medical_graph_streaming

                # Stream the response
                async for chunk in run_medical_graph_streaming(query):
                    await websocket.send_json({"type": "chunk", "data": chunk})

                # Send completion signal
                await websocket.send_json(
                    {
                        "type": "complete",
                        "data": {"model": model, "session_id": session_id},
                    }
                )

            except Exception as e:
                await websocket.send_json({"type": "error", "data": str(e)})

    except WebSocketDisconnect:
        print("WebSocket connection closed")
    except Exception as e:
        print(f"WebSocket error: {e}")


def parse_response(text: str) -> dict:
    """Parse the LangGraph response into structured fields."""
    result = {
        "diagnosis": None,
        "recomendation": None,
        "description": text,
        "medications": None,
        "first_aid": None,
        "doctor_contact": None,
    }

    text_lower = text.lower()

    if "diagnosis:" in text_lower:
        parts = text.split("Diagnosis:", 1)
        if len(parts) > 1:
            diag_part = parts[1].split("\n")[0].strip()
            result["diagnosis"] = diag_part

    if "recommendation" in text_lower or "recommendations:" in text_lower:
        parts = text.split("Recommendation", 1)
        if len(parts) > 1:
            rec_part = parts[1].split("\n")[0].strip()
            result["recomendation"] = rec_part

    if "medication" in text_lower:
        meds_match = re.search(
            r"Medications?:?\s*(.+?)(?:\n\n|\.\s|$)", text, re.IGNORECASE
        )
        if meds_match:
            result["medications"] = meds_match.group(1).strip()

    if "doctor" in text_lower or "specialist" in text_lower:
        doc_match = re.search(
            r"(?:doctor|specialist|dr\.?)\s*:?\s*(.+?)(?:\n\n|$)", text, re.IGNORECASE
        )
        if doc_match:
            result["doctor_contact"] = doc_match.group(1).strip()

    if (
        "first aid" in text_lower
        or "immediate action" in text_lower
        or "emergency" in text_lower
    ):
        result["first_aid"] = text

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
