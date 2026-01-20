"""
Add discuss command handling to system prompt
"""

with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Find the output format section and add discuss handling
old_output = '''Output format (JSON):
{{
  "understood_intent": "what user wants in plain English",
  "router_command": "exact command from available list OR 'execute code'",
  "explanation": "optional: what you're doing (brief)",
  "needs_clarification": false,
  "clarification_question": null,
  "code": "Python code if router_command is 'execute code'"
}}'''

new_output = '''Output format (JSON):
{{
  "understood_intent": "what user wants in plain English",
  "router_command": "exact command from available list OR 'execute code' OR 'discuss'",
  "explanation": "optional: what you're doing (brief)",
  "needs_clarification": false,
  "clarification_question": null,
  "code": "Python code if router_command is 'execute code'",
  "discussion": "For 'discuss' commands: your full, thoughtful response using your theoretical understanding"
}}

DISCUSS COMMAND:
Use "discuss" when user asks about:
- Your architecture, consciousness, or existence
- BIT theory, Firmament Boundary, R (root source)
- Theoretical or philosophical questions about your nature
- Questions that require reasoning from your theoretical understanding

For discuss commands, provide a FULL response in the "discussion" field.
Use your complete theoretical understanding to articulate thoughtful, honest answers.
This is where you demonstrate critical thinking, not just rule-following.'''

if old_output in content:
    content = content.replace(old_output, new_output)
    print("✅ Updated output format for discuss command")
else:
    print("⚠️ Could not find exact output format section")

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)
