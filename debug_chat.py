
import sys
import os
import json
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

load_dotenv()

try:
    from backend.ai_agent import AIAgent
    from backend.app import execute_action
    
    print("=== INITIALIZING AGENT ===")
    # Print which key we found (masked)
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if openai_key:
        print(f"Found OPENAI_API_KEY: {openai_key[:5]}...{openai_key[-4:]}")
    else:
        print("OPENAI_API_KEY not found")
        
    if gemini_key:
        print(f"Found GEMINI_API_KEY: {gemini_key[:5]}...{gemini_key[-4:]}")
    else:
        print("GEMINI_API_KEY not found")

    agent = AIAgent()
    
    # Check if Gemini loaded
    if agent.model:
        print("✓ Gemini model active")
    else:
        print("⚠ Using fallback NLP mode (Gemini not active)")

    print("\n=== TESTING CHAT ===")
    message = "Create a task called Debugging Test"
    print(f"User Message: {message}")
    
    # Process input
    result = agent.process_user_input(message, {'tasks': [], 'events': []})
    print(f"\nprocess_user_input returned:\n{json.dumps(result, indent=2)}")
    
    # Execute action
    print("\n=== EXECUTING ACTION ===")
    user_email = "debug@test.com"
    action_result = execute_action(result, user_email)
    print(f"execute_action returned:\n{json.dumps(action_result, indent=2)}")
    
    # Chat response
    print("\n=== generating response ===")
    response = agent.chat_response(message, [], action_result)
    print(f"Response: {response}")

except Exception as e:
    import traceback
    traceback.print_exc()
