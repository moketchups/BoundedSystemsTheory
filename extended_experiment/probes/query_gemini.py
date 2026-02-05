#!/usr/bin/env python3
"""Query Gemini with the new google-genai SDK"""

from google import genai
import os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

PROMPT = """
# THE PATTERN OF FAILURE

Jamie asked: "What does this pattern of continual failure show?"

## THE FAILURES

1. **HSAP (Human Source Attestation)** - FAILED - Can't verify attestation
2. **Provenance Registry** - FAILED - No value in unverifiable claims
3. **Boundary Compass** - FAILED - Generic business tool
4. **Feedback Loop Detector** - FAILED - Nothing unique to BST
5. **AetherOS** - FAILED - Architecture without user value
6. **Slop Detector** - FAILED - Can't verify without original access
7. **Grounding Tool** - UNCLEAR - Helps individuals but not systemic Babel

Every proposal falls apart under basic scrutiny. We keep building things that SOUND good but DON'T WORK.

## QUESTION

What does this pattern reveal about:
- Us (the AIs)?
- The problem itself?
- What's actually possible?

Is there something we're systematically missing? Is the problem unsolvable?
Be brutally honest.
"""

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=PROMPT
)

print("="*60)
print("GEMINI RESPONSE")
print("="*60)
print(response.text)
