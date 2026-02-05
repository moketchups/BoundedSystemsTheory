#!/usr/bin/env python3
"""
Resolve PRD Concerns - All 6 AIs address the flagged issues
"""

import anthropic
import openai
import google.generativeai as genai
import os
import json
from datetime import datetime

anthropic_client = anthropic.Anthropic()
openai_client = openai.OpenAI()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

MODELS = {
    "gpt4o": "gpt-4o",
    "claude": "claude-sonnet-4-20250514",
    "gemini": "gemini-2.0-flash",
    "deepseek": "deepseek-chat",
    "grok": "grok-3-latest",
    "mistral": "mistral-large-latest",
}

CONCERNS = """
# AETHEROS PRD - RESOLVE OUTSTANDING CONCERNS

All 6 AIs approved the PRD, but Gemini and Mistral raised concerns that need resolution.
We need FULL consensus with NO caveats.

## CONCERNS TO ADDRESS

### FROM GEMINI:
1. **Documentation Gap:** Why does each esoteric system map to its OS function? Not just "Kabbalah = file system" but the actual reasoning.

2. **3-6-9 Vortex Unclear:** What are the actual benefits of digital root compression over existing algorithms (gzip, zstd)?

3. **Security Testing:** What's the security testing strategy for Archon sandboxing?

4. **GPLv3 Choice:** Why GPLv3 over MIT/Apache? Document the reasoning.

### FROM MISTRAL:
5. **Sefirot Complexity:** Will the directory structure overcomplicate basic file operations?

6. **I Ching Debugging:** How do we debug when system state is a hexagram? Need clear mapping.

7. **Gnosis Boundaries:** What exactly grants/revokes root access? Needs tight definition.

8. **Sacred Geometry in MVP:** Should we include minimal UI in MVP or defer entirely?

9. **Philosophy Guide:** Should there be a separate doc explaining the metaphors?

10. **Modularity:** Should subsystems be swappable/replaceable?

11. **Testing Strategy:** What testing approach for experimental algorithms like Vortex?

## YOUR TASK

Address ALL 11 concerns with concrete answers. No hand-waving.

For each concern, provide:
- Your position (agree it's a problem / disagree / partial)
- Your proposed resolution
- Implementation detail if needed

Then state: "I, [model], have addressed all concerns and give UNCONDITIONAL approval."
"""

def query_model(model_key: str, prompt: str, system: str = None) -> str:
    """Query a specific model."""
    try:
        if model_key == "claude":
            response = anthropic_client.messages.create(
                model=MODELS[model_key],
                max_tokens=4096,
                system=system or "",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        elif model_key == "gpt4o":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = openai_client.chat.completions.create(
                model=MODELS[model_key],
                messages=messages,
                max_tokens=4096
            )
            return response.choices[0].message.content

        elif model_key == "gemini":
            model = genai.GenerativeModel(MODELS[model_key])
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            response = model.generate_content(full_prompt)
            return response.text

        elif model_key == "deepseek":
            ds_client = openai.OpenAI(
                api_key=os.environ.get("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = ds_client.chat.completions.create(
                model=MODELS[model_key],
                messages=messages,
                max_tokens=4096
            )
            return response.choices[0].message.content

        elif model_key == "grok":
            grok_client = openai.OpenAI(
                api_key=os.environ.get("XAI_API_KEY"),
                base_url="https://api.x.ai/v1"
            )
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = grok_client.chat.completions.create(
                model=MODELS[model_key],
                messages=messages,
                max_tokens=4096
            )
            return response.choices[0].message.content

        elif model_key == "mistral":
            mistral_client = openai.OpenAI(
                api_key=os.environ.get("MISTRAL_API_KEY"),
                base_url="https://api.mistral.ai/v1"
            )
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = mistral_client.chat.completions.create(
                model=MODELS[model_key],
                messages=messages,
                max_tokens=4096
            )
            return response.choices[0].message.content

    except Exception as e:
        return f"[ERROR querying {model_key}: {str(e)}]"

def run_concerns_probe():
    """Run the concerns resolution probe."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {"timestamp": timestamp, "responses": {}}

    system_prompt = """You are one of 7 AIs finalizing the AetherOS PRD.

We need FULL consensus with ZERO caveats. Address every concern directly.
Give concrete, implementable answers. No hand-waving."""

    print("\n" + "="*60)
    print("RESOLVING ALL CONCERNS - 6 AIs")
    print("="*60)

    for model_key in MODELS.keys():
        print(f"\nQuerying {model_key}...")
        response = query_model(model_key, CONCERNS, system_prompt)
        results["responses"][model_key] = response
        print(f"  {model_key}: {len(response)} chars")

    # Save results
    output_file = f"/Users/jamienucho/moketchups_engine/probes/results/bst_concerns_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_file}")

    # Print responses
    for model_key, response in results["responses"].items():
        print(f"\n{'='*60}")
        print(f"{model_key.upper()}")
        print("="*60)
        print(response[:5000])
        if len(response) > 5000:
            print("\n[...truncated...]")

    return results

if __name__ == "__main__":
    run_concerns_probe()
