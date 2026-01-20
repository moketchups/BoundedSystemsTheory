"""
Add discussion extraction to CognitiveOutput creation
"""

with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# The current line ends generated_code and closes the CognitiveOutput
old_line = '''generated_code=f"__result__ = ({generated_code})\\nif __result__ is not None:\\n    print(__result__)" if generated_code and not "print(" in generated_code else generated_code
            )'''

new_line = '''generated_code=f"__result__ = ({generated_code})\\nif __result__ is not None:\\n    print(__result__)" if generated_code and not "print(" in generated_code else generated_code,
                discussion=data.get("discussion")
            )'''

if old_line in content:
    content = content.replace(old_line, new_line)
    print("✅ Added discussion extraction")
else:
    print("⚠️ Could not find exact line - trying alternative")
    # Try simpler pattern
    if 'generated_code else generated_code\n            )' in content and 'discussion=data.get("discussion")' not in content:
        content = content.replace(
            'generated_code else generated_code\n            )',
            'generated_code else generated_code,\n                discussion=data.get("discussion")\n            )'
        )
        print("✅ Added discussion extraction (alternative method)")

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)
