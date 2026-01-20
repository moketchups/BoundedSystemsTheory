"""
Update response parsing to extract discussion field
"""

with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Find where we create CognitiveOutput and add discussion
old_return = '''            return CognitiveOutput(
                understood_intent=data.get("understood_intent", ""),
                router_command=data.get("router_command", "unknown"),
                explanation=data.get("explanation", ""),
                needs_clarification=data.get("needs_clarification", False),
                clarification_question=data.get("clarification_question", ""),
                generated_code=data.get("code", "")
            )'''

new_return = '''            return CognitiveOutput(
                understood_intent=data.get("understood_intent", ""),
                router_command=data.get("router_command", "unknown"),
                explanation=data.get("explanation", ""),
                needs_clarification=data.get("needs_clarification", False),
                clarification_question=data.get("clarification_question", ""),
                generated_code=data.get("code", ""),
                discussion=data.get("discussion", "")
            )'''

if old_return in content:
    content = content.replace(old_return, new_return)
    print("✅ Updated response parsing to extract discussion")
else:
    print("⚠️ Could not find exact return statement")

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)
