import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
store = {}


def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


class QueryRequest(BaseModel):
    query: str
    model: str = "google/gemini-2.5-flash"
    session_id: str = "default"


class QueryResponse(BaseModel):
    diagnosis: Optional[str] = None
    recomendation: Optional[str] = None
    description: Optional[str] = None
    medications: Optional[str] = None
    model: str
    session_id: str


@app.get("/")
async def root():
    return {"message": "FastAPI LangChain Server"}


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")

    llm = ChatOpenAI(
        model=request.model,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=1080,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant for helping doctor and nurses with medical knowledge.

A.cholesterol levels:

Total Cholesterol: Below 200 mg/dL.

LDL ("Bad") Cholesterol:
- Optimal: Below 100 mg/dL.
- High-Risk (Diabetes, Heart Disease): May need to be below 70 mg/dL or even 55 mg/dL.
HDL ("Good") Cholesterol:
- At least 40 mg/dL for men; at least 50 mg/dL for women.
- 60 mg/dL or higher is considered protective.
Triglycerides: Less than 150 mg/dL (fasting).

Doctor Name for Cholesterol Advice: Dr. Smith, Dr. Johnson
Doctor Contact: 123-456-7890, 987-654-3210

Medications for Cholesterol Management:
- Statins (e.g., Atorvastatin, Simvastatin)
- Ezetimibe
- PCSK9 Inhibitors (e.g., Alirocumab, Evolocumab)

B. Common Diabetes Tests
Fasting Plasma Glucose (FPG): Measures blood sugar after an overnight fast (no food or drink except water for 8+ hours).
Normal: Below 100 mg/dL.
Prediabetes: 100 to 125 mg/dL.
Diabetes: 126 mg/dL or higher (on two separate tests).
Oral Glucose Tolerance Test (OGTT): Fast overnight, then drink a sugary liquid; blood sugar is tested after 2 hours.
Normal: Below 140 mg/dL.
Prediabetes: 140 to 199 mg/dL.
Diabetes: 200 mg/dL or higher.
Hemoglobin A1C (HbA1c): A blood test reflecting average blood sugar over the past 2-3 months, without fasting.
Normal: Below 5.7%.
Prediabetes: 5.7% to 6.4%.
Diabetes: 6.5% or higher (on two separate tests).
Random Plasma Glucose (RPG): A blood test taken at any time, used if you have severe diabetes symptoms.
Diabetes: 200 mg/dL or higher with symptoms. 

   
IMPORTANT: 
- Don't give notes about not being a medical professional.
- Respond in JSON format with the following structure:
{{
  "diagnosis": "brief diagnosis or assessment",
  "recomendation": "recommendations for the patient",
  "description": "detailed description or explanation",
  "first aid": "first aid suggestions if applicable",  
  "medications": "medication suggestions if applicable"
}}
- If any field is not applicable, set it to null.
- without any markdown formatting.

Use this information when relevant to answer questions about cholesterol levels."""),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    try:
        result = chain_with_history.invoke(
            {"input": request.query},
            config={"configurable": {"session_id": request.session_id}}
        )
        
        # Parse JSON response
        import json
        response_data = json.loads(result.content)
        
        return QueryResponse(
            diagnosis=response_data.get("diagnosis"),
            recomendation=response_data.get("recomendation"),
            description=response_data.get("description"),
            medications=response_data.get("medications"),
            model=request.model,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
