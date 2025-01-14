import customtkinter as ctk
import tkinter as tk
from claude_api import ClaudeAPI
from datetime import datetime
import json

class ChatGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Claude Chat Interface")
        self.window.geometry("800x600")
        
        self.api = ClaudeAPI()
        self.conversation_id = self.api.create_conversation()
        
        self.setup_gui()
        
    def setup_gui(self):
        # Chat display
        self.chat_frame = ctk.CTkFrame(self.window)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.chat_display = ctk.CTkTextbox(self.chat_frame)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input area
        self.input_frame = ctk.CTkFrame(self.window)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.message_input = ctk.CTkTextbox(self.input_frame, height=100)
        self.message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to send message
        self.window.bind('<Return>', lambda event: self.send_message())
        
    def send_message(self):
        message = self.message_input.get("1.0", tk.END).strip()
        if not message:
            return
            
        # Display user message
        self.chat_display.insert(tk.END, f"You: {message}\n\n")
        self.message_input.delete("1.0", tk.END)
        
        # Get Claude's response
        response = self.api.send_message(message, conversation_id=self.conversation_id)
        
        # Display Claude's response
        self.chat_display.insert(tk.END, f"Claude: {response}\n\n")
        self.chat_display.see(tk.END)
        
    def run(self):
        self.window.mainloop()

def main():
    app = ChatGUI()
    app.run()

if __name__ == "__main__":
    main()
