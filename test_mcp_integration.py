"""
Test script for FastAPI server with MCP tools integration
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_root():
    """Test root endpoint"""
    print("=" * 70)
    print("Testing Root Endpoint")
    print("=" * 70)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_query(query: str, description: str):
    """Test query endpoint"""
    print("=" * 70)
    print(f"Test: {description}")
    print("=" * 70)
    print(f"Query: {query}")
    print()
    
    payload = {
        "query": query,
        "model": "anthropic/claude-3.5-sonnet",
        "session_id": "test_session"
    }
    
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nResponse:")
        print(f"  Diagnosis: {result.get('diagnosis')}")
        print(f"  Recommendation: {result.get('recomendation')}")
        print(f"  Description: {result.get('description')}")
        print(f"  Medications: {result.get('medications')}")
        print(f"  Model: {result.get('model')}")
        print(f"  Session: {result.get('session_id')}")
    else:
        print(f"Error: {response.text}")
    
    print()


def main():
    print("\n" + "=" * 70)
    print("FastAPI Server with MCP Tools - Integration Test")
    print("=" * 70)
    print()
    
    # Test 1: Root endpoint
    try:
        test_root()
    except Exception as e:
        print(f"Root test failed: {e}\n")
    
    # Test 2: Request cholesterol information
    try:
        test_query(
            "What are the normal cholesterol levels?",
            "Get Normal Cholesterol Levels"
        )
    except Exception as e:
        print(f"Test 2 failed: {e}\n")
    
    # Test 3: Diagnose cholesterol
    try:
        test_query(
            "I have total cholesterol 220, LDL 150, HDL 45, triglycerides 180. What does this mean?",
            "Diagnose Cholesterol Results"
        )
    except Exception as e:
        print(f"Test 3 failed: {e}\n")
    
    # Test 4: Diabetes risk assessment
    try:
        test_query(
            "My fasting glucose is 110 mg/dL and HbA1c is 6.0%. Am I at risk?",
            "Assess Diabetes Risk"
        )
    except Exception as e:
        print(f"Test 4 failed: {e}\n")
    
    # Test 5: Get medications
    try:
        test_query(
            "What medications are available for cholesterol?",
            "Get Cholesterol Medications"
        )
    except Exception as e:
        print(f"Test 5 failed: {e}\n")
    
    print("=" * 70)
    print("Tests Complete")
    print("=" * 70)


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║     MCP Integration Test - FastAPI + LangChain + MCP Tools      ║
    ║                                                                  ║
    ║  This script tests the FastAPI server that now uses MCP tools   ║
    ║  for medical information instead of hardcoded prompts.          ║
    ║                                                                  ║
    ║  Make sure the server is running:                               ║
    ║  $ uv run fastapi dev main.py                                   ║
    ║                                                                  ║
    ║  And OPENROUTER_API_KEY is set in .env                          ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server.")
        print("   Please make sure the server is running:")
        print("   $ uv run fastapi dev main.py\n")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.\n")
