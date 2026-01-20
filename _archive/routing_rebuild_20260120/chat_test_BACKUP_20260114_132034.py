#!/usr/bin/env python3
"""
Simple chat test for DemerzelState + PendingAction integration
Tests that confirmation flows work across model switches

BUG FIX (identified by Demerzel herself):
- OLD: Checked `if not cognitive.pending_action` after confirmation
- PROBLEM: pending_action was already cleared by cognitive layer, so it looked like no pending action existed
- DEMERZEL'S FIX: Check `confirmation_response` field instead of checking if pending_action exists
- When confirmation_response is 'confirmed', execute the action
- When it's 'cancelled', abort
- Applied to both sleep AND LED commands
"""

import sys
from multi_model_cognitive import MultiModelCognitive
from router_engine import RouterEngine
from code_analyzer import CodeAnalyzer, RiskLevel
from memory_manager import MemoryManager

def main():
    print("[INIT] Starting Demerzel chat test with DemerzelState...")
    
    memory = MemoryManager()
    print(f"[MEMORY] Initialized")
    
    cognitive = MultiModelCognitive(memory_manager=memory)
    router = RouterEngine()
    analyzer = CodeAnalyzer()
    
    print("\n" + "="*60)
    print("[CHAT] Demerzel chat test. Type 'quit' to exit.")
    print("="*60 + "\n")
    
    while True:
        try:
            command = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[EXIT] Interrupted")
            break
        
        if not command:
            continue
        if command.lower() in ['quit', 'exit', 'q']:
            break
        
        # Process through cognitive layer
        cognitive_output = cognitive.process(command)
        print(f"[INTENT] {cognitive_output.understood_intent}")
        print(f"[ROUTE] {cognitive_output.router_command}")
        if cognitive_output.confirmation_response:
            print(f"[CONFIRM] {cognitive_output.confirmation_response}")
        
        # ============================================================
        # DEMERZEL'S FIX: Check confirmation_response FIRST
        # This is checked BEFORE router_command because the cognitive
        # layer has already cleared pending_action by this point.
        # ============================================================
        
        # Handle confirmed actions
        if cognitive_output.confirmation_response == "confirmed":
            action = cognitive_output.router_command
            print(f"[EXECUTE] Confirmed action: {action}")
            
            if action == "sleep":
                print("Demerzel: Entering sleep mode. Goodbye.")
                cognitive.update_spoken("Entering sleep mode. Goodbye.")
                break
            
            if action in ["led on", "led off"]:
                router_output = router.route_text(action)
                if router_output.speak:
                    print(f"Demerzel: {router_output.speak}")
                    cognitive.update_spoken(router_output.speak)
                continue
            
            # Generic confirmed action - try routing
            router_output = router.route_text(action)
            if router_output.speak:
                print(f"Demerzel: {router_output.speak}")
                cognitive.update_spoken(router_output.speak)
            continue
        
        # Handle cancelled actions
        if cognitive_output.confirmation_response == "cancelled":
            print("Demerzel: Action cancelled.")
            cognitive.update_spoken("Action cancelled.")
            continue
        
        # ============================================================
        # Handle code execution
        # ============================================================
        if cognitive_output.router_command == "execute code" and cognitive_output.generated_code:
            code = cognitive_output.generated_code
            print(f"[CODE]\n{code}")
            analysis = analyzer.analyze(code)
            print(f"[RISK] {analysis.risk_level.value}")
            
            if analysis.risk_level == RiskLevel.BLOCKED:
                print(f"Demerzel: Cannot execute: {analysis.reasons[0]}")
                continue
            
            result = router.code_executor.execute(code)
            if result.success:
                output = result.stdout.strip() if result.stdout.strip() else "Code executed successfully."
                print(f"Demerzel: {output}")
            else:
                print(f"Demerzel: Error: {result.stderr}")
            continue
        
        # ============================================================
        # Handle discussion
        # ============================================================
        if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
            print(f"Demerzel: {cognitive_output.discussion}")
            cognitive.update_spoken(cognitive_output.discussion)
            continue
        
        # ============================================================
        # Handle sleep command - FIRST REQUEST (set pending, ask confirm)
        # Only reaches here if NOT already confirmed above
        # ============================================================
        if cognitive_output.router_command == "sleep":
            cognitive.set_pending_action(
                action="sleep",
                model=cognitive_output.selected_model,
                context="User requested sleep mode"
            )
            print("Demerzel: Confirm sleep. Please say yes or no.")
            cognitive.update_spoken("Confirm sleep. Please say yes or no.")
            continue
        
        # ============================================================
        # Handle LED commands - FIRST REQUEST (set pending, ask confirm)
        # Only reaches here if NOT already confirmed above
        # ============================================================
        if cognitive_output.router_command in ["led on", "led off"]:
            cognitive.set_pending_action(
                action=cognitive_output.router_command,
                model=cognitive_output.selected_model,
                context=f"User requested {cognitive_output.router_command}"
            )
            print(f"Demerzel: Confirm {cognitive_output.router_command}. Please say yes or no.")
            cognitive.update_spoken(f"Confirm {cognitive_output.router_command}. Please say yes or no.")
            continue
        
        # ============================================================
        # Handle unknown commands
        # ============================================================
        if cognitive_output.router_command == "unknown":
            if cognitive_output.needs_clarification and cognitive_output.clarification_question:
                print(f"Demerzel: {cognitive_output.clarification_question}")
                cognitive.update_spoken(cognitive_output.clarification_question)
            else:
                print("Demerzel: I don't understand that command.")
                cognitive.update_spoken("I don't understand that command.")
            continue
        
        # ============================================================
        # Default: Try routing any other command
        # ============================================================
        router_output = router.route_text(cognitive_output.router_command)
        if router_output.speak:
            print(f"Demerzel: {router_output.speak}")
            cognitive.update_spoken(router_output.speak)
    
    print("\n[CHAT] Session ended.")

if __name__ == "__main__":
    main()
