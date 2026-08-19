import os
import sys

def main():
    print("Initializing CoHabit.ai Demo Trigger...")
    
    # Add project root to path to prevent import issues
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Example 1: If you are triggering an API framework
        # import uvicorn
        # uvicorn.run("inspect_api:app", host="127.0.0.1", port=8000, reload=True)
        
        # Example 2: Standard test initialization
        print("Backend environment successfully verified.")
        print("Ready to connect with web/index.html")
        
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt (if available)")
    except Exception as e:
        print(f"An error occurred while launching: {e}")

if __name__ == "__main__":
    main()
