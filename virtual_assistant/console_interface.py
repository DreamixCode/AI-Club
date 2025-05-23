from agent import VirtualAssistant
import os

def main():
    # Create virtual assistant instance
    assistant = VirtualAssistant()
    
    print("Welcome! Type 'quit' to exit the conversation.")
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Exit condition
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
            
        # Process input and get response
        response = assistant.process_input(user_input)
        print(f"Assistant: {response}")

if __name__ == "__main__":
    main()
