
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.ai_agent import AIAgent
    print("Successfully imported AIAgent")
    
    # Try instantiation (will warn about missing API key but should succeed)
    agent = AIAgent()
    print("Successfully instantiated AIAgent")
    
    if agent.model:
        print("Gemini model initialized successfully")
    else:
        print("Gemini model not initialized (expected if no API key)")
        
except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")
