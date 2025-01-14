from claude_api import ClaudeAPI

def main():
    api = ClaudeAPI()
    
    print("Chat with Claude (type 'quit' to exit)")
    
    conversation_id = api.create_conversation()
    
    while True:
        message = input("You: ")
        if message.lower() == 'quit':
            break
            
        response = api.send_message(message, conversation_id=conversation_id)
        print(f"\nClaude: {response}\n")

if __name__ == "__main__":
    main()
