import anthropic
import os
import json
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ClaudeAPI:
    def __init__(self, store_conversations: bool = True):
        """
        Initialize the Claude API wrapper
        
        Args:
            store_conversations (bool): Whether to store conversation history in SQLite
        """
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.store_conversations = store_conversations
        
        # Default configuration
        self.config = {
            "model": "claude-3-sonnet-20240229",  # Latest model
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        if store_conversations:
            self.setup_conversation_storage()

    def setup_conversation_storage(self):
        """Set up SQLite database for conversation storage"""
        db_path = os.path.join('data', 'conversations.db')
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Create tables if they don't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT UNIQUE,
                created_at TIMESTAMP,
                last_updated TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                tokens INTEGER,
                timestamp TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def count_tokens(self, message: str) -> int:
        """Count tokens in message"""
        try:
            response = self.client.messages.count_tokens(
                messages=[{"role": "user", "content": message}]
            )
            return response.token_count
        except Exception as e:
            print(f"Error counting tokens: {str(e)}")
            return 0

    def create_conversation(self, metadata: Optional[Dict] = None) -> str:
        """Create a new conversation"""
        if not self.store_conversations:
            return None
            
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(os.path.join('data', 'conversations.db'))
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO conversations (conversation_id, created_at, last_updated, metadata)
            VALUES (?, ?, ?, ?)
        ''', (conversation_id, datetime.now(), datetime.now(), json.dumps(metadata or {})))
        
        conn.commit()
        conn.close()
        
        return conversation_id

    def add_message(self, conversation_id: str, role: str, content: str, tokens: int = None):
        """Add message to conversation history"""
        if not self.store_conversations:
            return
            
        conn = sqlite3.connect(os.path.join('data', 'conversations.db'))
        c = conn.cursor()
        
        if tokens is None:
            tokens = self.count_tokens(content)
        
        c.execute('''
            INSERT INTO messages (conversation_id, role, content, tokens, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (conversation_id, role, content, tokens, datetime.now()))
        
        c.execute('''
            UPDATE conversations 
            SET last_updated = ? 
            WHERE conversation_id = ?
        ''', (datetime.now(), conversation_id))
        
        conn.commit()
        conn.close()

    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Get message history for a conversation"""
        if not self.store_conversations:
            return []
            
        conn = sqlite3.connect(os.path.join('data', 'conversations.db'))
        df = pd.read_sql_query('''
            SELECT role, content, tokens, timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        ''', conn, params=(conversation_id,))
        conn.close()
        
        return df.to_dict('records')

    def send_message(self, message: str, conversation_id: Optional[str] = None,
                    system_prompt: Optional[str] = None) -> Union[str, Tuple[str, int]]:
        """Send message to Claude and get response"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            if conversation_id and self.store_conversations:
                history = self.get_conversation_history(conversation_id)
                messages.extend([{"role": msg["role"], "content": msg["content"]} 
                               for msg in history])
            
            messages.append({"role": "user", "content": message})
            
            response = self.client.messages.create(
                model=self.config["model"],
                max_tokens=self.config["max_tokens"],
                messages=messages
            )
            
            if conversation_id and self.store_conversations:
                self.add_message(conversation_id, "user", message)
                self.add_message(
                    conversation_id, 
                    "assistant", 
                    response.content[0].text
                )
            
            return response.content[0].text
            
        except Exception as e:
            error_msg = f"Error sending message: {str(e)}"
            print(error_msg)
            return error_msg

    def analyze_property(self, property_data: Dict) -> Dict:
        """Analyze a property using Claude"""
        prompt = f"""
        Please analyze this property listing and provide insights:
        
        Location: {property_data.get('area')}, {property_data.get('state')}
        Price: ${property_data.get('current_price', 0):,.2f}
        Type: {property_data.get('property_type')}
        Features: {property_data.get('features', '')}
        
        Please provide:
        1. Key property highlights
        2. Market position analysis
        3. Notable features and amenities
        4. Potential concerns or considerations
        """
        
        conv_id = self.create_conversation(metadata={
            "type": "property_analysis",
            "property_id": property_data.get("list_number")
        })
        
        analysis = self.send_message(prompt, conversation_id=conv_id)
        
        return {
            "analysis": analysis,
            "conversation_id": conv_id
        }

def main():
    api = ClaudeAPI()
    response = api.send_message("Hello, Claude! Please help me with MLS data analysis.")
    print(f"Response: {response}")
    
    conv_id = api.create_conversation(metadata={"type": "test"})
    
    responses = []
    for message in [
        "What are important factors in real estate analysis?",
        "How can we analyze market trends?",
        "What metrics should we track?"
    ]:
        response = api.send_message(message, conversation_id=conv_id)
        responses.append(response)
    
    history = api.get_conversation_history(conv_id)
    print("\nConversation History:")
    for msg in history:
        print(f"{msg['role']}: {msg['content'][:100]}...")

if __name__ == "__main__":
    main()
