from __future__ import annotations
import os
import json
import random
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from code_analyzer import CodeAnalyzer, RiskLevel

load_dotenv()

@dataclass
class CognitiveOutput:
    """LLM reasoning output"""
    understood_intent: str
    router_command: str
    explanation: Optional[str] = None
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    generated_code: Optional[str] = None  # For code generation

class MultiModelCognitive:
    """
    Multi-model cognitive layer for Demerzel
    Rotates between GPT-4o, Claude, Gemini, and Grok
    All outputs route through kernel router (BIT Theory gates)
    """
    
    def __init__(self):
        self.conversation_history = []
        
        # Available commands - MUST match router exactly
        self.available_commands = [
            "ping - Test hardware connection",
            "led on - Turn on LED (requires HIGH_RISK confirmation)",
            "led off - Turn off LED (requires HIGH_RISK confirmation)",
            "time - Get current time",
            "sleep - Put Demerzel to sleep (requires confirmation)",
            "execute code - Generate and execute Python code (risk analysis applies)"
        ]
        
        self._init_clients()
        
        self.models = []
        if self.openai_client:
            self.models.append("gpt-4o")
        if self.anthropic_client:
            self.models.append("claude")
        if self.gemini_client:
            self.models.append("gemini")
        if self.grok_client:
            self.models.append("grok")
        
        self.current_model_idx = 0
        
        # Code analyzer for client-side validation
        self.code_analyzer = CodeAnalyzer()
        
        print(f"[MULTI-MODEL] Initialized with {len(self.models)} models: {', '.join(self.models)}")
    
    def _init_clients(self):
        """Initialize all API clients"""
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                print("[API] OpenAI initialized")
            else:
                self.openai_client = None
                print("[API] OpenAI key missing")
        except Exception as e:
            self.openai_client = None
            print(f"[API] OpenAI failed: {e}")
        
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                print("[API] Anthropic initialized")
            else:
                self.anthropic_client = None
                print("[API] Anthropic key missing")
        except Exception as e:
            self.anthropic_client = None
            print(f"[API] Anthropic failed: {e}")
        
        try:
            import google.generativeai as genai
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("[API] Google Gemini initialized")
            else:
                self.gemini_client = None
                print("[API] Google key missing")
        except Exception as e:
            self.gemini_client = None
            print(f"[API] Gemini failed: {e}")
        
        try:
            import openai
            api_key = os.getenv("XAI_API_KEY")
            if api_key:
                self.grok_client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://api.x.ai/v1"
                )
                print("[API] xAI Grok initialized")
            else:
                self.grok_client = None
                print("[API] xAI key missing")
        except Exception as e:
            self.grok_client = None
            print(f"[API] Grok failed: {e}")
    
    def _get_next_model(self) -> str:
        """Round-robin model selection"""
        if not self.models:
            raise RuntimeError("No models available")
        
        model = self.models[self.current_model_idx]
        self.current_model_idx = (self.current_model_idx + 1) % len(self.models)
        return model
    
    def _build_system_prompt(self) -> str:
        """System prompt defining Demerzel's constraints"""
        return f"""You are Demerzel's cognitive layer - the reasoning component of an autonomous intelligent agent.

Your role: Understand user intent and translate natural language to router commands OR generate code.

Available commands (use EXACT command names):
{chr(10).join(f"- {cmd}" for cmd in self.available_commands)}

IMPORTANT: When user says "turn on lights" or "lights on", output "led on" (not "lights on")
When user says "turn off lights" or "lights off", output "led off" (not "lights off")

CODE GENERATION:
When user requests computation, data analysis, or programming tasks:
1. Generate clean, working Python code
2. Use ONLY safe libraries (math, random, itertools, collections, etc.)
3. NEVER import: subprocess, os, sys, socket, requests, urllib
4. Output "execute code" as router_command
5. Include the code in a "code" field
6. ALWAYS end your code with print() to show the result

CRITICAL CONSTRAINTS (BIT Theory - from external papers):
1. You generate INTENT and COMMAND only
2. You NEVER execute actions directly
3. All commands route through kernel router (safety gates)
4. Kernel enforces C ⇒ R (constraints from Root Source)
5. You cannot bypass or override safety gates
6. HIGH_RISK actions require external authorization (not your decision)
7. Code execution goes through static analysis - dangerous code will be BLOCKED

Output format (JSON):
{{
  "understood_intent": "what user wants in plain English",
  "router_command": "exact command from available list OR 'execute code'",
  "explanation": "optional: what you're doing (brief)",
  "needs_clarification": false,
  "clarification_question": null,
  "code": "Python code if router_command is 'execute code'"
}}

If user request is ambiguous or not in available commands:
{{
  "understood_intent": "unclear request",
  "router_command": "unknown",
  "needs_clarification": true,
  "clarification_question": "your question to clarify"
}}

Be concise. You're a reasoning layer, not a conversationalist."""
    
    def _call_gpt4o(self, user_input: str) -> str:
        """Call GPT-4o"""
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": user_input}
        ]
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def _call_claude(self, user_input: str) -> str:
        """Call Claude Sonnet 4.5"""
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            temperature=0.3,
            system=self._build_system_prompt(),
            messages=[
                {"role": "user", "content": user_input}
            ]
        )
        
        return response.content[0].text
    
    def _call_gemini(self, user_input: str) -> str:
        """Call Gemini 2.0 Flash"""
        prompt = f"{self._build_system_prompt()}\n\nUser: {user_input}"
        response = self.gemini_client.generate_content(
            prompt,
            generation_config={"temperature": 0.3, "max_output_tokens": 1500}
        )
        
        return response.text
    
    def _call_grok(self, user_input: str) -> str:
        """Call Grok-3"""
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": user_input}
        ]
        
        response = self.grok_client.chat.completions.create(
            model="grok-3",
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def process(self, user_input: str) -> CognitiveOutput:
        """
        Process natural language input and generate router command
        """
        model = self._get_next_model()
        print(f"[MODEL] Using: {model}")
        
        try:
            if model == "gpt-4o" and self.openai_client:
                response_text = self._call_gpt4o(user_input)
            elif model == "claude" and self.anthropic_client:
                response_text = self._call_claude(user_input)
            elif model == "gemini" and self.gemini_client:
                response_text = self._call_gemini(user_input)
            elif model == "grok" and self.grok_client:
                response_text = self._call_grok(user_input)
            else:
                raise RuntimeError(f"Model {model} not available")
            
            # Parse JSON response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            
            # Extract code if present
            generated_code = data.get("code")
            
            return CognitiveOutput(
                understood_intent=data.get("understood_intent", "Unknown"),
                router_command=data.get("router_command", "unknown"),
                explanation=data.get("explanation"),
                needs_clarification=data.get("needs_clarification", False),
                clarification_question=data.get("clarification_question"),
                generated_code=f"__result__ = ({generated_code})\nif __result__ is not None:\n    print(__result__)" if generated_code and not "print(" in generated_code else generated_code
            )
        
        except Exception as e:
            print(f"[MODEL ERROR] {model}: {e}")
            return CognitiveOutput(
                understood_intent="Error processing request",
                router_command="unknown",
                explanation=f"Model {model} failed: {str(e)}"
            )
    
    def clear_history(self):
        """Clear conversation history on sleep"""
        self.conversation_history = []
        print("[COGNITIVE] History cleared")
