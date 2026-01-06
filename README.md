# Cholesterol and Blood Sugar Test Helper

A Python application to help track and analyze cholesterol and blood sugar test results.

## Features

- Analyze test results against standard health ranges
- Generate health recommendations based on test values

## Installation

first, create .env file and fill in OPENROUTER_API_KEY

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd python_interview

# Or use uv sync if you have a pyproject.toml
uv sync

#run 
uv run fastapi dev main.py
```

Server will be available at <http://127.0.0.1:8000>

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
