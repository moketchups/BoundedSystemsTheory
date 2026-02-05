#!/usr/bin/env python3
"""Get missing PRD responses from Gemini and Mistral"""

import anthropic
import openai
import google.generativeai as genai
import os
import json
from datetime import datetime

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Load existing PRD responses
with open("/Users/jamienucho/moketchups_engine/probes/results/bst_prd_20260203_144852.json") as f:
    existing = json.load(f)

round1_responses = existing["rounds"][0]["responses"]

CONTEXT = """
# AETHEROS PRD - FINAL CONSENSUS REVIEW

The other AIs have submitted their PRD drafts. Here's a summary of what they agreed on:

## CONSENSUS FROM GPT-4o, CLAUDE, DEEPSEEK, GROK:

**Product Name:** AetherOS

**One-Line:** A research operating system that implements core computing primitives through bounded, testable metaphors from symbolic systems.

**7 Subsystems:**
1. KABBALAH (kernel-sefirot) - Kernel + File System with Sefirot directory structure
2. I CHING (telemetry-hexagram) - 64 hexagram system state monitoring
3. SACRED GEOMETRY (compositor-metatron) - Flower of Life UI rendering
4. GNOSTICISM (security-pleroma) - Archon sandboxes, Gnosis root access
5. 3-6-9 VORTEX (codec-vortex) - Digital root compression/hashing
6. PHOENIX (mm-phoenix) - Three-zone memory management (Nest/Flight/Ash)
7. ARK (storage-ark) - Immutable backup snapshots

**Tech Stack:** Rust (kernel), C (telemetry), C++ (rendering), Python (tools)

**License:** GPLv3

**MVP:** Bootable QEMU system with Sefirot-FS, ichingd telemetry, basic Archon sandboxing

## YOUR TASK

Review this consensus. Do you agree? 

Write your FINAL approval statement including:
1. Do you approve the name "AetherOS"? (Yes/No, or suggest alternative)
2. Do you approve the 7-subsystem architecture? (Yes/No, any modifications?)
3. Do you approve the MVP scope? (Yes/No, any changes?)
4. Any critical additions or concerns?

End with: "I, [model name], [APPROVE/DO NOT APPROVE] this unified PRD."
"""

def query_gemini(prompt, system):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        full_prompt = f"{system}\n\n{prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"[ERROR: {str(e)}]"

def query_mistral(prompt, system):
    try:
        client = openai.OpenAI(
            api_key=os.environ.get("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1"
        )
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="mistral-large-latest",
            messages=messages,
            max_tokens=4096
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR: {str(e)}]"

system = """You are one of 7 AIs finalizing the AetherOS PRD.
The other 4 AIs have reached consensus. Review and provide your final approval or concerns."""

print("="*60)
print("GETTING MISSING APPROVALS")
print("="*60)

print("\nQuerying Gemini...")
gemini_response = query_gemini(CONTEXT, system)
print(f"  Gemini: {len(gemini_response)} chars")

print("\nQuerying Mistral...")
mistral_response = query_mistral(CONTEXT, system)
print(f"  Mistral: {len(mistral_response)} chars")

print("\n" + "="*60)
print("GEMINI RESPONSE")
print("="*60)
print(gemini_response)

print("\n" + "="*60)
print("MISTRAL RESPONSE")  
print("="*60)
print(mistral_response)

# Save
results = {
    "gemini": gemini_response,
    "mistral": mistral_response,
    "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
}
with open("/Users/jamienucho/moketchups_engine/probes/results/bst_prd_missing.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n\nResults saved.")
