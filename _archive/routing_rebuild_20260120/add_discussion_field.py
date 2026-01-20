"""
Add discussion field to CognitiveOutput dataclass
"""

with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Add discussion field after generated_code
old_field = '    generated_code: Optional[str] = None  # For code generation'
new_field = '''    generated_code: Optional[str] = None  # For code generation
    discussion: Optional[str] = None  # Full response for theoretical queries'''

if old_field in content and 'discussion: Optional[str]' not in content:
    content = content.replace(old_field, new_field)
    print("✅ Added discussion field to CognitiveOutput")
else:
    if 'discussion: Optional[str]' in content:
        print("✅ discussion field already exists")
    else:
        print("⚠️ Could not find insertion point")

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)
