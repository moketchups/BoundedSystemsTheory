with open('multi_model_cognitive.py', 'r') as f:
    content = f.read()

# Add memory parameter to __init__
old = '''    def __init__(self):
        self.conversation_history = []'''

new = '''    def __init__(self, memory_manager=None):
        self.conversation_history = []
        self.memory = memory_manager'''

content = content.replace(old, new)

# Update system prompt to include memory context
old = '''    def _build_system_prompt(self) -> str:
        """System prompt defining Demerzel's constraints"""
        return f"""You are Demerzel's cognitive layer - the reasoning component of an autonomous intelligent agent.'''

new = '''    def _build_system_prompt(self, context: str = "") -> str:
        """System prompt defining Demerzel's constraints"""
        context_section = f"""
RECENT CONVERSATION CONTEXT:
{context}
""" if context else ""
        
        return f"""You are Demerzel's cognitive layer - the reasoning component of an autonomous intelligent agent.

{context_section}'''

content = content.replace(old, new)

# Update process method to get memory context
old = '''    def process(self, user_input: str) -> CognitiveOutput:
        """
        Process natural language input and generate router command
        """
        model = self._get_next_model()
        print(f"[MODEL] Using: {model}")'''

new = '''    def process(self, user_input: str) -> CognitiveOutput:
        """
        Process natural language input and generate router command
        """
        # Get memory context if available
        context = ""
        if self.memory:
            context = self.memory.get_context_summary(max_turns=5)
        
        model = self._get_next_model()
        print(f"[MODEL] Using: {model}")'''

content = content.replace(old, new)

# Update all model calls to use context
for model_func in ['_call_gpt4o', '_call_claude', '_call_gemini', '_call_grok']:
    old_pattern = f'''    def {model_func}(self, user_input: str) -> str:'''
    new_pattern = f'''    def {model_func}(self, user_input: str, context: str = "") -> str:'''
    content = content.replace(old_pattern, new_pattern)

# Update system prompt calls in all model functions
content = content.replace(
    'system=self._build_system_prompt(),',
    'system=self._build_system_prompt(context),'
)
content = content.replace(
    '{"role": "system", "content": self._build_system_prompt()}',
    '{"role": "system", "content": self._build_system_prompt(context)}'
)
content = content.replace(
    'prompt = f"{self._build_system_prompt()}\\n\\nUser: {user_input}"',
    'prompt = f"{self._build_system_prompt(context)}\\n\\nUser: {user_input}"'
)

# Update model call invocations to pass context
content = content.replace(
    'response_text = self._call_gpt4o(user_input)',
    'response_text = self._call_gpt4o(user_input, context)'
)
content = content.replace(
    'response_text = self._call_claude(user_input)',
    'response_text = self._call_claude(user_input, context)'
)
content = content.replace(
    'response_text = self._call_gemini(user_input)',
    'response_text = self._call_gemini(user_input, context)'
)
content = content.replace(
    'response_text = self._call_grok(user_input)',
    'response_text = self._call_grok(user_input, context)'
)

with open('multi_model_cognitive.py', 'w') as f:
    f.write(content)

print("✅ Added memory context to cognitive layer")
