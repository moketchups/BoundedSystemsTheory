#!/usr/bin/env python3
"""
PROPER FIX: Intent-based model selection with learning

This patch:
1. Adds pre-classification to detect intent BEFORE model selection
2. Detects explicit model requests ("use Grok", "ask Claude")
3. Passes real intent to SmartModelSelector
4. Calls record_outcome after each response for learning

Run: cd ~/demerzel && python3 proper_fix.py
"""

from pathlib import Path
import re

def main():
    print("=" * 60)
    print("PROPER FIX: Intent + Learning Integration")
    print("=" * 60)
    
    f = Path("multi_model_cognitive.py")
    if not f.exists():
        print("[ERROR] multi_model_cognitive.py not found")
        return False
    
    c = f.read_text()
    original = c
    changes = []
    
    # === FIX 1: Add pre-classification method ===
    preclassify_method = '''
    def _preclassify_intent(self, user_input: str) -> tuple[str, str]:
        """
        Quick intent classification BEFORE model selection.
        Returns (intent_type, forced_model or None)
        
        This lets us route to the right model WITHOUT calling an LLM first.
        """
        text = user_input.lower()
        
        # Check for explicit model requests
        model_patterns = {
            "grok": [r"\\buse grok\\b", r"\\bask grok\\b", r"\\bgrok.?s turn\\b", r"\\blet grok\\b"],
            "claude": [r"\\buse claude\\b", r"\\bask claude\\b", r"\\bclaude.?s turn\\b", r"\\blet claude\\b"],
            "gemini": [r"\\buse gemini\\b", r"\\bask gemini\\b", r"\\bgemini.?s turn\\b", r"\\blet gemini\\b"],
            "gpt-4o": [r"\\buse gpt\\b", r"\\bask gpt\\b", r"\\bgpt.?s turn\\b", r"\\buse openai\\b"],
        }
        
        forced_model = None
        for model, patterns in model_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    forced_model = model
                    print(f"[PRE-CLASSIFY] User requested: {model}")
                    break
            if forced_model:
                break
        
        # Classify intent type
        if any(kw in text for kw in ["execute", "run", "code", "script", "python", "write code"]):
            intent = "execute code"
        elif any(kw in text for kw in ["search", "look up", "find", "google", "who is", "what is"]):
            intent = "search"
        elif any(kw in text for kw in ["status", "health", "model", "which model", "are you working"]):
            intent = "status"
        elif any(kw in text for kw in ["create", "make", "build", "generate"]):
            intent = "create"
        elif any(kw in text for kw in ["explain", "why", "how does", "tell me about"]):
            intent = "explain"
        else:
            intent = "discuss"
        
        print(f"[PRE-CLASSIFY] Intent: {intent}")
        return intent, forced_model
'''
    
    # Add after _init_clients method (find a good spot)
    if "_preclassify_intent" not in c:
        # Add before _select_model
        marker = "    def _select_model(self"
        if marker in c:
            c = c.replace(marker, preclassify_method + "\n" + marker, 1)
            changes.append("Added _preclassify_intent method")
        else:
            print("[WARN] Could not find _select_model to insert before")
    else:
        print("[OK] _preclassify_intent already exists")
    
    # === FIX 2: Update process() to use pre-classification ===
    
    # Find and replace the model selection in process()
    old_selection = '''        # Select model
        model = self._select_model(intent="confirmation", force_model=force_model)'''
    
    new_selection = '''        # PROPER FIX: Pre-classify intent and detect forced model
        preclassified_intent, user_forced_model = self._preclassify_intent(user_input)
        
        # User's explicit model request overrides confirmation routing
        if user_forced_model:
            force_model = user_forced_model
        
        # Select model based on actual intent
        model = self._select_model(intent=preclassified_intent, force_model=force_model)'''
    
    if old_selection in c:
        c = c.replace(old_selection, new_selection, 1)
        changes.append("Updated process() to use pre-classification")
    elif "preclassified_intent, user_forced_model" in c:
        print("[OK] process() already uses pre-classification")
    else:
        print("[WARN] Could not find model selection block to replace")
    
    # === FIX 3: Add learning (record_outcome) after successful response ===
    
    old_success = '''                # SUCCESS - record it and process
                self._record_model_success(model)'''
    
    new_success = '''                # SUCCESS - record it and process
                self._record_model_success(model)
                
                # LEARNING: Record outcome for SmartModelSelector
                router_cmd = data.get("router_command", "unknown")
                self.model_selector.record_outcome(model, router_cmd, success=True)'''
    
    if old_success in c and "self.model_selector.record_outcome" not in c:
        c = c.replace(old_success, new_success, 1)
        changes.append("Added learning on success (record_outcome)")
    elif "self.model_selector.record_outcome" in c:
        print("[OK] Learning already wired in")
    else:
        print("[WARN] Could not find success block to add learning")
    
    # === FIX 4: Add learning on failure too ===
    
    old_failure_json = '''            except json.JSONDecodeError as e:
                last_error = f"JSON parse failed - {e}"
                print(f"[MODEL ERROR] {model}: {last_error}")
                self._record_model_failure(model)'''
    
    new_failure_json = '''            except json.JSONDecodeError as e:
                last_error = f"JSON parse failed - {e}"
                print(f"[MODEL ERROR] {model}: {last_error}")
                self._record_model_failure(model)
                self.model_selector.record_outcome(model, preclassified_intent, success=False, notes=last_error)'''
    
    if old_failure_json in c and "record_outcome(model, preclassified_intent, success=False" not in c:
        c = c.replace(old_failure_json, new_failure_json, 1)
        changes.append("Added learning on JSON failure")
    
    old_failure_general = '''            except Exception as e:
                last_error = str(e)
                print(f"[MODEL ERROR] {model}: {last_error}")
                self._record_model_failure(model)'''
    
    new_failure_general = '''            except Exception as e:
                last_error = str(e)
                print(f"[MODEL ERROR] {model}: {last_error}")
                self._record_model_failure(model)
                self.model_selector.record_outcome(model, preclassified_intent, success=False, notes=last_error)'''
    
    if old_failure_general in c and c.count("record_outcome(model, preclassified_intent, success=False") < 2:
        c = c.replace(old_failure_general, new_failure_general, 1)
        changes.append("Added learning on general failure")
    
    # === FIX 5: Add 'import re' if not present (needed for preclassify) ===
    if "import re" not in c:
        c = c.replace("import json", "import json\nimport re", 1)
        changes.append("Added import re")
    
    # === WRITE ===
    if c != original:
        # Backup first
        from datetime import datetime
        backup = f"multi_model_cognitive_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        Path(backup).write_text(original)
        print(f"[OK] Backed up to: {backup}")
        
        f.write_text(c)
        print(f"[OK] Wrote fixed file")
        print()
        print("Changes made:")
        for change in changes:
            print(f"  ✓ {change}")
    else:
        print("[INFO] No changes needed")
    
    # === VERIFY ===
    print()
    print("=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    final = f.read_text()
    checks = [
        ("_preclassify_intent method", "_preclassify_intent"),
        ("Pre-classification used in process()", "preclassified_intent, user_forced_model"),
        ("Learning on success", "record_outcome(model, router_cmd, success=True)"),
        ("Learning on failure", "record_outcome(model, preclassified_intent, success=False"),
        ("Model forcing works", "user_forced_model"),
    ]
    
    all_pass = True
    for name, pattern in checks:
        if pattern in final:
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name}")
            all_pass = False
    
    print()
    if all_pass:
        print("=" * 60)
        print("FIX COMPLETE")
        print("=" * 60)
        print()
        print("Test with:")
        print("  python3 chat_test.py")
        print()
        print("Then try:")
        print('  "use Grok to answer this"')
        print('  "what is 2+2"')
        print('  "execute this code: print(hello)"')
        print()
        print("Watch for:")
        print("  [PRE-CLASSIFY] Intent: ...")
        print("  [PRE-CLASSIFY] User requested: ...")
        print("  [MODEL SELECT] intent → model")
        print("  [LEARNING] model + task = SUCCESS/FAILURE")
    else:
        print("=" * 60)
        print("FIX INCOMPLETE - check warnings above")
        print("=" * 60)
    
    return all_pass


if __name__ == "__main__":
    main()
