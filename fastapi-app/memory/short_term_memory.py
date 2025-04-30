from typing import Dict

session_memory: Dict[str, Dict[str, str]] = {}

def add_to_short_term_memory(session_id: str, user_prompt: str, assistant_response: str):
    session_memory[session_id] = {
        "user_prompt": user_prompt,
        "assistant_response": assistant_response
    }

def get_short_term_memory(session_id: str):
    return session_memory.get(session_id)