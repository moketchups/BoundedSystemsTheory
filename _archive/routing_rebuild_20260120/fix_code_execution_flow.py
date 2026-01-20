with open('brain_controller.py', 'r') as f:
    content = f.read()

# Remove the continue after code execution and add stay-awake there
old = '''                    print(f"[CODE OUTPUT] {output}")
                    response = f"Code executed successfully. Result: {output[:100]}"
                    speak(tts, response)
                    # Store code execution in memory
                    memory.store_conversation("demerzel", response, 
                                            intent="CODE_EXECUTION",
                                            executed=True)
                else:
                    error = result.stderr.strip()
                    print(f"[CODE ERROR] {error}")
                    response = f"Code execution failed. {error[:100]}"
                    speak(tts, response)
                    # Store code error in memory
                    memory.store_conversation("demerzel", response,
                                            intent="CODE_EXECUTION_ERROR",
                                            executed=False)
                
                continue'''

new = '''                    print(f"[CODE OUTPUT] {output}")
                    response = f"Code executed successfully. Result: {output[:100]}"
                    speak(tts, response)
                    # Store code execution in memory
                    memory.store_conversation("demerzel", response, 
                                            intent="CODE_EXECUTION",
                                            executed=True)
                else:
                    error = result.stderr.strip()
                    print(f"[CODE ERROR] {error}")
                    response = f"Code execution failed. {error[:100]}"
                    speak(tts, response)
                    # Store code error in memory
                    memory.store_conversation("demerzel", response,
                                            intent="CODE_EXECUTION_ERROR",
                                            executed=False)
                
                # Stay awake for follow-up after code execution
                print("[VOICE] Staying awake for follow-up...")
                time.sleep(1)
                
                follow_up = transcribe_command(recognizer, stream, timeout=5.0)
                if follow_up:
                    command = follow_up
                    print(f"[COGNITIVE] Processing follow-up: '{command}'")
                    
                    # Store user input
                    memory.store_conversation("user", command)
                    
                    # Process follow-up
                    cognitive_output = cognitive.process(command)
                    print(f"[COGNITIVE] Intent: {cognitive_output.understood_intent}")
                    print(f"[COGNITIVE] Command: {cognitive_output.router_command}")
                    
                    # Check if it's another code request
                    if cognitive_output.router_command == "execute code" and cognitive_output.generated_code:
                        # Loop back to code execution
                        code = cognitive_output.generated_code
                        print(f"[CODE GENERATED]\n{code}")
                        
                        analysis = analyzer.analyze(code)
                        print(f"[CODE ANALYSIS] Risk: {analysis.risk_level.value}")
                        
                        if analysis.risk_level == RiskLevel.BLOCKED:
                            speak(tts, f"I cannot execute this code. {analysis.reasons[0]}")
                            continue
                        
                        if analysis.risk_level == RiskLevel.HIGH:
                            speak(tts, "This code has high risk. Say yes to proceed.")
                            confirm = transcribe_command(recognizer, stream, timeout=5.0)
                            if "yes" not in confirm.lower():
                                speak(tts, "Cancelled.")
                                continue
                        
                        result = router.code_executor.execute(code)
                        if result.success:
                            lines = result.stdout.strip().split("\\n")
                            output_lines = [l for l in lines if not l.startswith("[FILE SYSTEM]")]
                            output = "\\n".join(output_lines).strip() or "(no output)"
                            response = f"Code executed successfully. Result: {output[:100]}"
                        else:
                            response = f"Code execution failed. {result.stderr[:100]}"
                        
                        speak(tts, response)
                        memory.store_conversation("demerzel", response, intent="CODE_EXECUTION", executed=result.success)
                        continue
                    else:
                        # Route through normal flow
                        router_output = router.route_text(cognitive_output.router_command)
                        print(f"[RESULT] intent={router_output.intent}, executed={router_output.did_execute}")
                        
                        if router_output.speak:
                            speak(tts, router_output.speak)
                            memory.store_conversation("demerzel", router_output.speak,
                                                    intent=str(router_output.intent),
                                                    executed=router_output.did_execute)
                
                continue'''

content = content.replace(old, new)

with open('brain_controller.py', 'w') as f:
    f.write(content)

print("✅ Fixed code execution follow-up flow")
