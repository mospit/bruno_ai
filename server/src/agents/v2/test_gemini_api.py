import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
config_path = Path(__file__).parent.parent.parent.parent / "config" / ".env"
load_dotenv(dotenv_path=config_path)

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")
print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"API Key prefix: {api_key[:10]}..." if api_key else "None")

# Test the API
try:
    genai.configure(api_key=api_key)
    
    # List available models
    print("\nAvailable models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")
    
    # Try with gemini-1.5-flash which is commonly available
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Hello, Bruno AI is working!'")
    print(f"\nAPI Test Result: {response.text}")
except Exception as e:
    print(f"\nAPI Test Failed: {type(e).__name__}: {str(e)}")
    print("\nThis suggests the API key may be invalid or there's a connection issue.")
