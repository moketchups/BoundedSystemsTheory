with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Find the code generation section in system prompt
old_text = """CODE GENERATION:
When user requests computation, data analysis, or programming tasks:
1. Generate clean, working Python code
2. Use ONLY safe libraries (math, random, itertools, collections, etc.)
3. NEVER import: subprocess, os, sys, socket, requests, urllib
4. Output "execute code" as router_command
5. Include the code in a "code" field"""

new_text = """CODE GENERATION:
When user requests computation, data analysis, or programming tasks:
1. Generate clean, working Python code
2. Use ONLY safe libraries (math, random, itertools, collections, etc.)
3. NEVER import: subprocess, os, sys, socket, requests, urllib
4. Output "execute code" as router_command
5. Include the code in a "code" field
6. ALWAYS end your code with print() to show the result"""

content = content.replace(old_text, new_text)

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)

print("Updated: LLM will now generate code with print() statements")
