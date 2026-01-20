"""
Add discussion field to CognitiveOutput
"""

with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Find CognitiveOutput class and add discussion field
old_class = '''@dataclass
class CognitiveOutput:
    understood_intent: str
    router_command: str
    explanation: str = ""
    needs_clarification: bool = False
    clarification_question: str = ""
    generated_code: str = ""'''

new_class = '''@dataclass
class CognitiveOutput:
    understood_intent: str
    router_command: str
    explanation: str = ""
    needs_clarification: bool = False
    clarification_question: str = ""
    generated_code: str = ""
    discussion: str = ""  # Full response for theoretical/philosophical queries'''

if old_class in content:
    content = content.replace(old_class, new_class)
    print("✅ Added discussion field to CognitiveOutput")
else:
    print("⚠️ Could not find exact CognitiveOutput class")
    # Check if discussion already exists
    if 'discussion: str' in content:
        print("   discussion field already exists")

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)
