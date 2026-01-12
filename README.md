# Cholesterol and Blood Sugar Test Helper

A Python application to help track and analyze cholesterol and blood sugar test results. Now includes an MCP (Model Context Protocol) server implementation with FastMCP and full LangChain integration.

## Features

- Analyze test results against standard health ranges
- Generate health recommendations based on test values
- **MCP Server**: Expose medical tools via Model Context Protocol
- **LangChain Integration**: Use MCP tools with LangChain agents for intelligent medical assistance
- **FastAPI Server with MCP**: Main API server now uses MCP tools for all medical queries

## Installation

First, create .env file and fill in OPENROUTER_API_KEY

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd hospital_management

# Install dependencies
uv sync
```

## Running the Application

### FastAPI Server (Recommended)

The main FastAPI server now integrates with MCP tools:

```bash
# Start the server
uv run fastapi dev main.py
```

Server will be available at <http://127.0.0.1:8000>

**What's Different:**

- The server now uses MCP tools from `mcp_server.py`
- LangChain agent decides which tools to call
- More accurate and maintainable than prompt-based approach
- See [MCP_INTEGRATION_CHANGES.md](MCP_INTEGRATION_CHANGES.md) for details

### Testing the FastAPI Server

```bash
# In another terminal (server must be running)
uv run python test_mcp_integration.py
```

This will test various medical queries using the MCP-integrated endpoint.

## MCP Server Usage

### Quick Start - Simple Demo

Try the simple MCP demo without requiring API keys:

```bash
# Run local demonstration
uv run python mcp_demo_simple.py demo

# Run as MCP server (stdio mode)
uv run python mcp_demo_simple.py
```

The simple demo shows:

- Basic MCP server structure with FastMCP
- Tool definitions and resource handling
- How MCP servers expose functionality

### Running the Full MCP Server

The MCP server provides medical information tools that can be accessed via the Model Context Protocol:

```bash
# Run MCP server (stdio mode)
uv run python mcp_server.py

# Or run with FastMCP CLI for inspection
uv run fastmcp run mcp_server.py
```

### Available MCP Tools

The server exposes the following tools:

- `get_cholesterol_levels()` - Get normal cholesterol level ranges
- `get_cholesterol_doctors()` - Get doctor contact information
- `get_cholesterol_medications()` - List cholesterol medications
- `get_diabetes_test_info(test_type)` - Get diabetes test information
- `diagnose_cholesterol(total, ldl, hdl, triglycerides)` - Diagnose cholesterol levels
- `calculate_diabetes_risk(fpg, hba1c)` - Calculate diabetes risk

### MCP Resources

- `medical://guidelines/cholesterol` - Cholesterol management guidelines
- `medical://guidelines/diabetes` - Diabetes testing and management guidelines

## LangChain Demo

Run the demonstration of using MCP tools with LangChain:

```bash
# Run the demo (requires OPENROUTER_API_KEY in .env)
uv run python demo_mcp_langchain.py
```

The demo includes:

- Automated queries showing various use cases
- Interactive mode for asking your own medical questions
- Integration with Claude 3.5 Sonnet via OpenRouter

### Example Usage

```python
from demo_mcp_langchain import run_demo
import asyncio

# Run the demo
asyncio.run(run_demo())
```

The agent can:

- Answer questions about cholesterol and diabetes
- Analyze test results using the MCP tools
- Provide medical recommendations
- Look up medication information

## Health Reference Ranges

### Cholesterol (mg/dL)

- **Total**: < 200 (Desirable), 200-239 (Borderline), ≥ 240 (High)
- **LDL**: < 100 (Optimal), 100-129 (Near optimal), 130-159 (Borderline), ≥ 160 (High)
- **HDL**: ≥ 60 (Desirable), 40-59 (Acceptable), < 40 (Low)
- **Triglycerides**: < 150 (Normal), 150-199 (Borderline), ≥ 200 (High)

### Blood Sugar (mg/dL)

- **Fasting**: < 100 (Normal), 100-125 (Prediabetes), ≥ 126 (Diabetes)
- **Post-meal**: < 140 (Normal), 140-199 (Prediabetes), ≥ 200 (Diabetes)
- **HbA1c (%)**: < 5.7 (Normal), 5.7-6.4 (Prediabetes), ≥ 6.5 (Diabetes)

## Requirements

- Python 3.8+
- uv (recommended) or pip for package management
- Dependencies listed in `requirements.txt` or `pyproject.toml`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

no license

## Disclaimer

This tool is for educational and tracking purposes only. Always consult with healthcare professionals for medical advice and diagnosis.
