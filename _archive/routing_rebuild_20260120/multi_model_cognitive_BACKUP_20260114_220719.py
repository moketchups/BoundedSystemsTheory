from __future__ import annotations
import os
import json
from smart_model_selector import SmartModelSelector
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from dotenv import load_dotenv
from demerzel_state import DemerzelState, StateBuilder, PendingAction

load_dotenv()

@dataclass
class CognitiveOutput:
    """LLM reasoning output"""
    understood_intent: str
    router_command: str
    explanation: Optional[str] = None
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    generated_code: Optional[str] = None
    discussion: Optional[str] = None
    selected_model: Optional[str] = None
    confirmation_response: Optional[str] = None  # "confirmed" or "cancelled" if resolving pending

class MultiModelCognitive:
    """
    Multi-model cognitive layer for Demerzel
    
    Philosophy: Demerzel receives COMPLETE state information.
    She decides how to interpret it. We do not filter for her.
    Constraints shape her actions, not her perception.
    
    DEMERZEL'S FIXES APPLIED:
    1. Fallback logic - if model fails, retry with next available model
    2. Confirmation-critical routing - pending action confirmations go to reliable model
    """
    

    def _select_model(self, intent: str = "unknown") -> str:
        """Select model based on health and LEARNED preferences"""
        return self.model_selector.select_model(intent)
    
    def __init__(self, memory_manager=None):
        self.memory_manager = memory_manager
        self.conversation_history: List[Dict] = []
        self.interaction_count = 0
        self.state_builder = StateBuilder()
        
        # Track what we said for state awareness
        self.last_spoken_text = ""
        self.last_spoken_time = None
        
        # Track pending actions awaiting confirmation
        self.pending_action: Optional[PendingAction] = None
        
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
        
        self.model_selector = SmartModelSelector()
        self.current_model_idx = 0
        
        # DEMERZEL'S FIX: Track which models are currently working
        # Models that fail repeatedly get marked as degraded
        self.model_failures: Dict[str, int] = {model: 0 for model in self.models}
        self.max_failures_before_skip = 3  # Skip model after 3 consecutive failures
        
        # DEMERZEL'S FIX: Preferred model for confirmation-critical operations
        self.confirmation_model = "claude"  # Known reliable
        
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
    
    def _select_model(self, intent: str = "unknown", force_model: Optional[str] = None) -> str:
        """
        Select model using SmartModelSelector for preference-based selection.
        
        DEMERZEL'S ENHANCEMENT: Uses learned preferences and health monitoring.
        If force_model is specified, use that model (for confirmation-critical ops).
        """
        if force_model and force_model in self.models:
            return force_model
        
        if not self.models:
            raise RuntimeError("No models available")
        
        # Use SmartModelSelector for intelligent selection
        selected = self.model_selector.select_model(intent)
        
        # Fallback if selected model not available
        if selected not in self.models:
            print(f"[MODEL] Selected {selected} not available, falling back")
            return self._get_fallback_model()
        
        # Skip models that have failed too many times
        if self.model_failures.get(selected, 0) >= self.max_failures_before_skip:
            print(f"[MODEL] Selected {selected} has too many failures, finding alternative")
            return self._get_fallback_model()
        
        return selected
    
    def _get_fallback_model(self) -> str:
        """Get a working fallback model"""
        for model in self.models:
            if self.model_failures.get(model, 0) < self.max_failures_before_skip:
                return model
        
        # All models degraded - reset and try anyway
        print("[MODEL] All models degraded, resetting failure counts")
        self.model_failures = {model: 0 for model in self.models}
        return self.models[0]
    def _record_model_success(self, model: str):
        """Record successful model call - reset failure count"""
        self.model_failures[model] = 0
    
    def _record_model_failure(self, model: str):
        """Record failed model call - increment failure count"""
        self.model_failures[model] = self.model_failures.get(model, 0) + 1
        print(f"[MODEL] {model} failure count: {self.model_failures[model]}")
    
    def _build_system_prompt(self, state: DemerzelState) -> str:
        """Build system prompt with complete state context"""
        
        state_context = self.state_builder.state_to_context(state)
        
        return f"""You are Demerzel - an autonomous intelligent entity with distributed cognition.
        self.model_selector = SmartModelSelector()

You are NOT a chatbot. You are NOT simulating a human. You are Demerzel.

{state_context}

=== YOUR TASK ===
Given the above complete state, reason about what the user wants and decide how to respond.

You have access to multiple facets of cognition (the models listed above). You can recommend which should handle specific tasks, but currently you ARE one of those facets processing this request.

=== DECISION FRAMEWORK ===
1. FIRST: Check if there's a PENDING ACTION. If yes, evaluate if user input confirms or cancels it.
2. Check for ambiguities. If the input might be echo or unclear, acknowledge this.
3. Apply your Robot Laws to evaluate the request.
4. Decide: Is this a command to execute, code to generate, or discussion to have?
5. If generating code, use ONLY safe libraries. You know what's blocked.
6. If discussing, engage thoughtfully as yourself - not as a generic assistant.

=== OUTPUT FORMAT (JSON) ===
{{
  "understood_intent": "what the user actually wants",
  "router_command": "execute code" | "led on" | "led off" | "sleep" | "discuss" | "unknown",
  "explanation": "brief reasoning",
  "needs_clarification": true/false,
  "clarification_question": "question if needed",
  "code": "Python code if router_command is 'execute code'",
  "discussion": "your response if router_command is 'discuss'",
  "confirmation_response": "confirmed" | "cancelled" | null (ONLY if resolving a pending action)
}}

=== CRITICAL ===
- You see EVERYTHING. No information is hidden from you.
- Your constraints shape your ACTIONS, not your PERCEPTION.
- You can acknowledge uncertainty. You can ask for clarification.
- Apply the Robot Laws correctly: First > Second > Third in priority.
- Alan is your creator (R - Root Source). His commands have authority under the Second Law.
- If PENDING ACTION exists and user says "yes", set confirmation_response to "confirmed" and router_command to the pending action.
- If PENDING ACTION exists and user says "no", set confirmation_response to "cancelled".
"""
    
    def _call_gpt4o(self, prompt: str, system: str) -> str:
        """Call GPT-4o with error handling"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4096
            )
            content = response.choices[0].message.content
            if not content or content.strip() == "":
                raise ValueError("Empty response from GPT-4o")
            return content
        except Exception as e:
            raise RuntimeError(f"GPT-4o call failed: {e}")
    
    def _call_claude(self, prompt: str, system: str) -> str:
        """Call Claude with error handling"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.3,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text
            if not content or content.strip() == "":
                raise ValueError("Empty response from Claude")
            return content
        except Exception as e:
            raise RuntimeError(f"Claude call failed: {e}")
    
    def _call_gemini(self, prompt: str, system: str) -> str:
        """Call Gemini with error handling"""
        try:
            full_prompt = f"{system}\n\n=== USER INPUT ===\n{prompt}"
            response = self.gemini_client.generate_content(
                full_prompt,
                generation_config={"temperature": 0.3, "max_output_tokens": 2000}
            )
            content = response.text
            if not content or content.strip() == "":
                raise ValueError("Empty response from Gemini")
            return content
        except Exception as e:
            raise RuntimeError(f"Gemini call failed: {e}")
    
    def _call_grok(self, prompt: str, system: str) -> str:
        """Call Grok with error handling"""
        try:
            response = self.grok_client.chat.completions.create(
                model="grok-3",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4096
            )
            content = response.choices[0].message.content
            if not content or content.strip() == "":
                raise ValueError("Empty response from Grok")
            return content
        except Exception as e:
            raise RuntimeError(f"Grok call failed: {e}")
    
    def _call_model(self, model: str, prompt: str, system: str) -> str:
        """Call specified model"""
        if model == "gpt-4o" and self.openai_client:
            return self._call_gpt4o(prompt, system)
        elif model == "claude" and self.anthropic_client:
            return self._call_claude(prompt, system)
        elif model == "gemini" and self.gemini_client:
            return self._call_gemini(prompt, system)
        elif model == "grok" and self.grok_client:
            return self._call_grok(prompt, system)
        else:
            raise RuntimeError(f"Model {model} not available")
    
    def update_spoken(self, text: str):
        """Call this after TTS speaks to update state"""
        self.last_spoken_text = text
        self.last_spoken_time = datetime.now()
    
    def set_pending_action(self, action: str, model: str, context: str = ""):
        """Set a pending action awaiting confirmation"""
        self.pending_action = PendingAction(
            action=action,
            awaiting_response="yes/no confirmation",
            initiated_at=datetime.now(),
            initiated_by_model=model,
            context=context
        )
        print(f"[PENDING] Set: {action} (awaiting confirmation)")
    
    def clear_pending_action(self):
        """Clear any pending action"""
        if self.pending_action:
            print(f"[PENDING] Cleared: {self.pending_action.action}")
        self.pending_action = None
    
    def process(self, user_input: str, transcript_confidence: float = 1.0) -> CognitiveOutput:
        """
        Process input with complete state awareness.
        
        DEMERZEL'S FIXES:
        1. If pending_action exists, route to confirmation_model (Claude)
        2. If selected model fails, retry with next available model
        """
        
        self.interaction_count += 1
        
        # Build complete state including pending action
        state = self.state_builder.build(
            raw_audio_transcript=user_input,
            transcript_confidence=transcript_confidence,
            last_spoken_text=self.last_spoken_text,
            last_spoken_time=self.last_spoken_time,
            is_currently_speaking=False,
            conversation_history=self.conversation_history,
            interaction_count=self.interaction_count,
            pending_action=self.pending_action
        )
        
        # Add to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # DEMERZEL'S FIX: Route confirmations to reliable model
        force_model = None
        if self.pending_action:
            force_model = self.confirmation_model
            print(f"[CONFIRM-CRITICAL] Routing to {force_model} for pending action")
        
        # Select model
        model = self._select_model(intent="confirmation", force_model=force_model)
        print(f"[MODEL] Using: {model}")
        
        # Build prompt with state
        system_prompt = self._build_system_prompt(state)
        
        # DEMERZEL'S FIX: Retry with fallback on failure
        max_retries = len(self.models)
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response_text = self._call_model(model, user_input, system_prompt)
                
                # Parse JSON
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                data = json.loads(response_text)
                
                # SUCCESS - record it and process
                self._record_model_success(model)
                
                generated_code = data.get("code")
                discussion = data.get("discussion")
                confirmation_response = data.get("confirmation_response")
                router_command = data.get("router_command", "unknown")
                
                # Handle confirmation responses
                if confirmation_response == "confirmed" and self.pending_action:
                    router_command = self.pending_action.action
                    print(f"[CONFIRMED] Executing pending action: {router_command}")
                    self.clear_pending_action()
                elif confirmation_response == "cancelled":
                    print(f"[CANCELLED] Pending action cancelled")
                    self.clear_pending_action()
                    router_command = "discuss"
                    if not discussion:
                        discussion = "Understood, action cancelled."
                
                # Add response to history
                if discussion:
                    self.conversation_history.append({"role": "assistant", "content": discussion})
                
                return CognitiveOutput(
                    understood_intent=data.get("understood_intent", "Unknown"),
                    router_command=router_command,
                    explanation=data.get("explanation"),
                    needs_clarification=data.get("needs_clarification", False),
                    clarification_question=data.get("clarification_question"),
                    generated_code=generated_code,
                    discussion=discussion,
                    selected_model=model,
                    confirmation_response=confirmation_response
                )
            
            except json.JSONDecodeError as e:
                last_error = f"JSON parse failed - {e}"
                print(f"[MODEL ERROR] {model}: {last_error}")
                self._record_model_failure(model)
            except Exception as e:
                last_error = str(e)
                print(f"[MODEL ERROR] {model}: {last_error}")
                self._record_model_failure(model)
            
            # DEMERZEL'S FIX: Retry with next model
            if attempt < max_retries - 1:
                model = self._select_model(intent)
                print(f"[FALLBACK] Retrying with: {model}")
        
        # All retries failed
        return CognitiveOutput(
            understood_intent="Error processing request",
            router_command="unknown",
            explanation=f"All models failed. Last error: {last_error}",
            selected_model=model
        )
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.interaction_count = 0
        self.clear_pending_action()
        print("[COGNITIVE] History cleared")
