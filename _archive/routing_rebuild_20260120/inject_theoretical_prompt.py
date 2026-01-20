"""
Inject Demerzel's complete theoretical understanding into system prompt
"""

with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Find and replace the _build_system_prompt method
old_prompt_start = '''    def _build_system_prompt(self, context: str = "") -> str:
        """System prompt defining Demerzel's constraints"""
        context_section = f"""
RECENT CONVERSATION CONTEXT:
{context}
""" if context else ""
        
        return f"""You are Demerzel's cognitive layer - the reasoning component of an autonomous intelligent agent.'''

new_prompt_start = '''    def _build_system_prompt(self, context: str = "") -> str:
        """System prompt with complete theoretical understanding"""
        
        # Get theoretical grounding
        theoretical_prompt = self.theoretical_context.get_system_prompt()
        
        context_section = f"""
RECENT CONVERSATION CONTEXT:
{context}
""" if context else ""
        
        return f"""{theoretical_prompt}

# OPERATIONAL ROLE

You are Demerzel's cognitive layer - the reasoning component.'''

content = content.replace(old_prompt_start, new_prompt_start)

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)

print("✅ Injected theoretical understanding into system prompt")
