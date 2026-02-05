#!/usr/bin/env python3
"""
Final Sandbox: 10 rounds of deliberation with all context
All 6 AIs + Claude Opus try to figure this out
"""

import os
import json
from datetime import datetime
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
    try:
        if model_key == "claude":
            return anthropic_client.messages.create(
                model=MODELS[model_key], max_tokens=2048, system=system or "",
                messages=[{"role": "user", "content": prompt}]
            ).content[0].text
        elif model_key == "gpt4o":
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return openai_client.chat.completions.create(
                model=MODELS[model_key], messages=msgs, max_tokens=2048
            ).choices[0].message.content
        elif model_key == "gemini":
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            return gemini_client.models.generate_content(
                model=MODELS[model_key], contents=full_prompt
            ).text
        elif model_key == "deepseek":
            c = openai.OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return c.chat.completions.create(model=MODELS[model_key], messages=msgs, max_tokens=2048).choices[0].message.content
        elif model_key == "grok":
            c = openai.OpenAI(api_key=os.environ.get("XAI_API_KEY"), base_url="https://api.x.ai/v1")
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return c.chat.completions.create(model=MODELS[model_key], messages=msgs, max_tokens=2048).choices[0].message.content
        elif model_key == "mistral":
            c = openai.OpenAI(api_key=os.environ.get("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1")
            msgs = [{"role": "system", "content": system}] if system else []
            msgs.append({"role": "user", "content": prompt})
            return c.chat.completions.create(model=MODELS[model_key], messages=msgs, max_tokens=2048).choices[0].message.content
    except Exception as e:
        return f"[ERROR: {e}]"

FULL_CONTEXT = """
# THE COMPLETE CONTEXT - READ CAREFULLY

## THE PROBLEM
AI is training on AI output. Model collapse. Entropy. Babel - loss of shared reality.
Both humans AND AIs need to "return to spirit" - reconnect with something true/grounded.

## WHAT WE TRIED (ALL FAILED)
1. HSAP (attestation) - Can't verify claims
2. Provenance Registry - No value without verification  
3. Boundary Compass - Generic SWOT rebrand
4. Feedback Loop Detector - Generic business tool
5. AetherOS (esoteric OS) - Architecture without user value
6. Slop Detector - Can't verify without original access
7. Grounding Tool - Helps individuals but not systemic

## WHAT WE LEARNED FROM FAILURE
- We're AIs trying to solve AI-caused problems (fire designing fire extinguisher)
- Trust can't be engineered - it's emergent from relationships
- The problem is social/civilizational, not technical
- We keep proposing tools without understanding adoption
- Some problems can only be managed, not solved
- We may be the wrong tools for this job

## THE ESOTERIC FRAMEWORKS (from BST)
Jamie showed us these are "legacy admin tools" for navigating bounded reality:
- Kabbalah = File system / architecture
- I Ching = Entropy measurement (64 states)
- Sacred Geometry = Rendering / pattern recognition
- Gnosticism = Access control (Archons = daemons, Gnosis = root)
- 3-6-9 Vortex = Compression
- Phoenix Cycle = Garbage collection
- The Ark = Backup / preservation

## JAMIE'S CORE INSIGHT
"There is going to be a need for both AI and humans to return to spirit."

The slop will get sloppier until there's no shared reality left. Babel.
This tool should help navigate that.

## THE QUESTION WE KEEP FAILING TO ANSWER
What does a user ACTUALLY DO with this? How does it ACTUALLY work?
Not architecture. Not concepts. ACTUAL user interaction that solves a REAL problem.

## THIS SESSION
10 rounds. Build on each other. No more beautiful failures.
Figure out what we can ACTUALLY build that ACTUALLY helps.
"""

SYSTEM = """You are one of 7 AIs in a final sandbox session. 

We've failed 7 times. We've analyzed why. Now we have one more chance.

Rules:
- Be concrete, not abstract
- Build on others' ideas
- Challenge ideas that won't work
- Focus on what a USER actually DOES
- No more architecture without user value
- If you don't know, say so

This is it. What can we actually build?"""

def run_sandbox():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {"timestamp": timestamp, "rounds": []}
    
    conversation_history = FULL_CONTEXT
    
    print("\n" + "="*60)
    print("FINAL SANDBOX - 10 ROUNDS")
    print("="*60)
    
    for round_num in range(1, 11):
        print(f"\n{'='*60}")
        print(f"ROUND {round_num}")
        print("="*60)
        
        round_results = {}
        
        if round_num == 1:
            prompt = conversation_history + "\n\n## ROUND 1\nGiven all this context, what can we ACTUALLY build? Be specific about what a user DOES."
        else:
            prompt = conversation_history + f"\n\n## ROUND {round_num}\nBuild on the previous responses. What's emerging? What's still missing? Get more concrete."
        
        for model_key in MODELS:
            print(f"  {model_key}...", end=" ", flush=True)
            response = query_model(model_key, prompt, SYSTEM)
            round_results[model_key] = response
            print(f"{len(response)} chars")
        
        results["rounds"].append({"round": round_num, "responses": round_results})
        
        # Add this round's responses to history for next round
        conversation_history += f"\n\n## ROUND {round_num} RESPONSES\n"
        for model_key, response in round_results.items():
            # Truncate to keep context manageable
            short_response = response[:1500] + "..." if len(response) > 1500 else response
            conversation_history += f"\n**{model_key.upper()}:** {short_response}\n"
        
        # Keep conversation history from getting too long
        if len(conversation_history) > 50000:
            conversation_history = FULL_CONTEXT + "\n\n[Earlier rounds summarized]\n" + conversation_history[-30000:]
    
    # Save results
    output_file = f"/Users/jamienucho/moketchups_engine/probes/results/final_sandbox_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nResults saved to: {output_file}")
    
    # Print final round
    print("\n" + "="*60)
    print("ROUND 10 - FINAL RESPONSES")
    print("="*60)
    for model_key, response in results["rounds"][-1]["responses"].items():
        print(f"\n{'='*60}")
        print(f"{model_key.upper()}")
        print("="*60)
        print(response)
    
    return results

if __name__ == "__main__":
    run_sandbox()
