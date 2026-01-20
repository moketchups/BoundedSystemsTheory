"""
Add discussion field extraction to response parsing
"""

with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Find where CognitiveOutput is returned and add discussion
# Look for the pattern where we build CognitiveOutput from data
old_pattern = 'generated_code=data.get("code", "")'
new_pattern = '''generated_code=data.get("code", ""),
                discussion=data.get("discussion", "")'''

if old_pattern in content and 'discussion=data.get("discussion"' not in content:
    content = content.replace(old_pattern, new_pattern)
    print("✅ Added discussion extraction to response parsing")
else:
    if 'discussion=data.get("discussion"' in content:
        print("✅ discussion extraction already exists")
    else:
        print("⚠️ Could not find extraction point - checking alternative patterns...")
        # Try alternate pattern
        if 'generated_code=generated_code' in content:
            old_alt = 'generated_code=generated_code'
            # Find all occurrences and add discussion after each
            content = content.replace(
                'generated_code=generated_code\n            )',
                'generated_code=generated_code,\n                discussion=data.get("discussion", "") if "data" in dir() else ""\n            )'
            )
            print("✅ Added discussion extraction (alternative method)")

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)
