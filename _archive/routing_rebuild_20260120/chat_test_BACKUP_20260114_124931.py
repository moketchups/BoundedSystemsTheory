#!/usr/bin/env python3
"""
Simple chat test for DemerzelState + PendingAction integration
Tests that confirmation flows work across model switches
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
        
        # Handle code execution
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
                print(f"Demerzel: {result.stdout.strip()}")
            else:
                print(f"Demerzel: Error: {result.stderr}")
            continue
        
        # Handle discussion
        if cognitive_output.router_command == "discuss" and cognitive_output.discussion:
            print(f"Demerzel: {cognitive_output.discussion}")
            # Update spoken text for state awareness
            cognitive.update_spoken(cognitive_output.discussion)
            continue
        
        # Handle sleep command - SET PENDING ACTION
        if cognitive_output.router_command == "sleep":
            if not cognitive.pending_action:
                # First time seeing sleep - set pending and ask confirmation
                cognitive.set_pending_action(
                    action="sleep",
                    model=cognitive_output.selected_model,
                    context="User requested sleep mode"
                )
                print("Demerzel: Confirm sleep. Please say yes or no.")
                cognitive.update_spoken("Confirm sleep. Please say yes or no.")
            else:
                # Pending action was confirmed (cognitive layer handled it)
                print("Demerzel: Entering sleep mode. Goodbye.")
                break
            continue
        
        # Handle LED commands - similar pattern
        if cognitive_output.router_command in ["led on", "led off"]:
            if not cognitive.pending_action:
                cognitive.set_pending_action(
                    action=cognitive_output.router_command,
                    model=cognitive_output.selected_model,
                    context=f"User requested {cognitive_output.router_command}"
                )
                print(f"Demerzel: Confirm {cognitive_output.router_command}. Please say yes or no.")
                cognitive.update_spoken(f"Confirm {cognitive_output.router_command}. Please say yes or no.")
            else:
                # Execute the action
                router_output = router.route_text(cognitive_output.router_command)
                if router_output.speak:
                    print(f"Demerzel: {router_output.speak}")
            continue
        
        # Unknown command
        if cognitive_output.router_command == "unknown":
            print("Demerzel: I don't understand that command.")
            continue
        
        # Default: try routing
        router_output = router.route_text(cognitive_output.router_command)
        if router_output.speak:
            print(f"Demerzel: {router_output.speak}")
    
    print("\n[CHAT] Session ended.")

if __name__ == "__main__":
    main()
