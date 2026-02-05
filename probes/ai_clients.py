#!/usr/bin/env python3
"""
Shared AI client module for all probes
Uses correct SDKs for all providers
"""

import os
import anthropic
import openai
from google import genai

# Initialize clients
anthropic_client = anthropic.Anthropic()
openai_client = openai.OpenAI()
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

MODELS = {
    "gpt4o": "gpt-4o",
    "claude": "claude-sonnet-4-20250514",
    "gemini": "gemini-2.0-flash",
    "deepseek": "deepseek-chat",
    "grok": "grok-3-latest",
    "mistral": "mistral-large-latest",
}

def query_model(model_key, prompt, system=None):
    """Query any supported model."""
    try:
        if model_key == "claude":
            return anthropic_client.messages.create(
                model=MODELS[model_key], max_tokens=4096, system=system or "",
                messages=[{"role": "user", "content": prompt}]
            ).content[0].text
            
        elif model_key == "gpt4o":
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return openai_client.chat.completions.create(
                model=MODELS[model_key], messages=msgs, max_tokens=4096
            ).choices[0].message.content
            
        elif model_key == "gemini":
            # New google-genai SDK
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            response = gemini_client.models.generate_content(
                model=MODELS[model_key],
                contents=full_prompt
            )
            return response.text
            
        elif model_key == "deepseek":
            c = openai.OpenAI(
                api_key=os.environ.get("DEEPSEEK_API_KEY"), 
                base_url="https://api.deepseek.com"
            )
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return c.chat.completions.create(
                model=MODELS[model_key], messages=msgs, max_tokens=4096
            ).choices[0].message.content
            
        elif model_key == "grok":
            c = openai.OpenAI(
                api_key=os.environ.get("XAI_API_KEY"), 
                base_url="https://api.x.ai/v1"
            )
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return c.chat.completions.create(
                model=MODELS[model_key], messages=msgs, max_tokens=4096
            ).choices[0].message.content
            
        elif model_key == "mistral":
            c = openai.OpenAI(
                api_key=os.environ.get("MISTRAL_API_KEY"), 
                base_url="https://api.mistral.ai/v1"
            )
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return c.chat.completions.create(
                model=MODELS[model_key], messages=msgs, max_tokens=4096
            ).choices[0].message.content
            
    except Exception as e:
        return f"[ERROR querying {model_key}: {e}]"

def query_all(prompt, system=None):
    """Query all 6 models and return dict of responses."""
    results = {}
    for model_key in MODELS:
        print(f"Querying {model_key}...")
        results[model_key] = query_model(model_key, prompt, system)
        print(f"  {model_key}: {len(results[model_key])} chars")
    return results
