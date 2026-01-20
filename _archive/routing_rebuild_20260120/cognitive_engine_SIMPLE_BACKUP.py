"""
Cognitive Engine: LLM-powered reasoning layer for Demerzel
Sits between perception (voice/vision) and kernel router
"""
from __future__ import annotations
import json
from typing import Optional
from dataclasses import dataclass

@dataclass
class CognitiveContext:
    """Context passed to LLM for reasoning"""
    user_input: str
    conversation_history: list[dict]
    available_commands: list[str]
    current_state: dict

@dataclass  
class CognitiveOutput:
    """LLM reasoning output"""
    understood_intent: str
    router_command: str
    explanation: Optional[str] = None
    needs_clarification: bool = False
    clarification_question: Optional[str] = None

class CognitiveEngine:
    """LLM-powered reasoning for natural language understanding"""
    
    def __init__(self):
        self.conversation_history = []
        
        # Available commands Demerzel can execute
        self.available_commands = [
            "ping - Test hardware connection",
            "led on - Turn on LED (requires HIGH_RISK confirmation)",
            "led off - Turn off LED (requires HIGH_RISK confirmation)", 
            "lights on - Same as 'led on'",
            "lights off - Same as 'led off'",
            "time - Get current time",
            "sleep - Put Demerzel to sleep (requires confirmation)"
        ]
    
    def process(self, user_input: str) -> CognitiveOutput:
        """
        Process natural language input and generate router command
        
        For now: Simple keyword matching (Phase 2a)
        Later: Full LLM integration (Phase 2b)
        """
        user_input = user_input.strip().lower()
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Simple intent matching for now
        # We'll upgrade to LLM API in next step
        
        if "light" in user_input or "led" in user_input:
            if "on" in user_input or "turn on" in user_input:
                return CognitiveOutput(
                    understood_intent="User wants to turn on lights",
                    router_command="led on",
                    explanation="Turning on the LED"
                )
            elif "off" in user_input or "turn off" in user_input:
                return CognitiveOutput(
                    understood_intent="User wants to turn off lights",
                    router_command="led off",
                    explanation="Turning off the LED"
                )
        
        if "ping" in user_input or "test" in user_input:
            return CognitiveOutput(
                understood_intent="User wants to test hardware",
                router_command="ping",
                explanation="Testing hardware connection"
            )
        
        if "time" in user_input or "what time" in user_input:
            return CognitiveOutput(
                understood_intent="User wants to know the time",
                router_command="time",
                explanation="Getting current time"
            )
        
        if "sleep" in user_input or "go to sleep" in user_input or "goodnight" in user_input:
            return CognitiveOutput(
                understood_intent="User wants Demerzel to sleep",
                router_command="sleep",
                explanation="Preparing to sleep"
            )
        
        # Unknown intent
        return CognitiveOutput(
            understood_intent="Unknown",
            router_command="unknown",
            needs_clarification=True,
            clarification_question="I'm not sure what you want me to do. Available commands: " + 
                                  ", ".join(cmd.split(" - ")[0] for cmd in self.available_commands)
        )
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
