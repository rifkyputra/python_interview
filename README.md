# Medical AI Assistant

Modern medical triage and education stack combining FastAPI, LangGraph, MCP tools, and a streaming React UI. The project routes natural-language questions into structured medical logic for cholesterol and diabetes, and exposes the same tools through Model Context Protocol for agent interoperability.

## Highlights
- FastAPI API with LangGraph decisioning to classify, diagnose, and format medical responses
- MCP server (FastMCP) exporting the same medical tools for external agents
- Streaming WebSocket chat UI (Vite/React/TypeScript) that talks to the FastAPI backend
- Ready-to-run dev setup with `uv` for Python dependencies and Vite for the frontend
- Bonus NestJS service scaffold (`hospital_management/`) for future integrations

## Architecture
- Python core logic in [medical_core/](medical_core) (cholesterol and diabetes calculators, first-aid guidance)
- LangGraph flow in [langgraph_app.py](langgraph_app.py) orchestrates tools and risk checks
- FastAPI app in [main.py](main.py) exposes `/query` HTTP + `/ws/query` WebSocket for streaming replies
- MCP server in [mcp_server.py](mcp_server.py) publishes the same tools over stdio/CLI via FastMCP
- Frontend in [medical-ai-ui/](medical-ai-ui) connects to `ws://localhost:8000/ws/query` for live responses

## Quickstart
1) Prereqs: Python 3.10+, `uv` installed, Node 18+ with npm or pnpm.
2) Clone and create `.env` in the repo root with `OPENROUTER_API_KEY=<your-key>` for OpenRouter (Gemini).
3) Backend setup:
```bash
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
4) Frontend (chat UI):
```bash
cd medical-ai-ui
npm install   # or pnpm install
npm run dev -- --host --port 5173
```
Open the UI at http://localhost:5173 while the FastAPI server is running; it streams over `ws://localhost:8000/ws/query`.
5) Optional MCP server (stdio):
```bash
uv run python mcp_server.py
# or inspect with FastMCP CLI
uv run fastmcp run mcp_server.py
```
6) Optional NestJS scaffold:
```bash
cd hospital_management
pnpm install
pnpm start:dev
```

## API Surface (FastAPI)
- `GET /` health/meta
- `POST /query` — JSON body: `{ "query": "What do I do with LDL 170?", "model": "google/gemini-3-flash-preview", "session_id": "demo" }`
- `WS /ws/query` — send `{ "query": "Explain high triglycerides", "model": "google/gemini-3-flash-preview", "session_id": "demo" }` and receive `status` → `chunk` → `complete` messages for streaming UX.

## MCP Tools (FastMCP)
- `get_cholesterol_levels_mcp()` — normal ranges and guidance
- `get_cholesterol_doctors_mcp()` — specialist directory
- `get_cholesterol_medications_mcp()` — medication classes
- `get_diabetes_test_info_mcp(test_type="all")` — test ranges and notes
- `diagnose_cholesterol_mcp(total, ldl, hdl, triglycerides)` — rule-based diagnosis
- `calculate_diabetes_risk_mcp(fpg=None, hba1c=None)` — diabetes risk estimation

## Health Reference Ranges
**Cholesterol (mg/dL)**: Total < 200 desirable; LDL < 100 optimal; HDL ≥ 60 desirable; Triglycerides < 150 normal.

**Blood Sugar (mg/dL)**: Fasting < 100 normal; Post-meal < 140 normal; HbA1c < 5.7 normal.

## Testing
- Backend integration smoke: `uv run python test_mcp_integration.py` (requires server running on :8000)
- Frontend lint/build: `npm run lint` and `npm run build` inside `medical-ai-ui`
- Nest service tests (if used): `pnpm test` inside `hospital_management`

## Tech Stack
- FastAPI, Uvicorn, LangGraph, LangChain OpenAI adapter, FastMCP
- React 18, Vite, TypeScript, Zustand, Tailwind
- NestJS 11 scaffold for future hospital modules

## Disclaimer
Educational prototype only. Not a substitute for professional medical advice, diagnosis, or treatment.
