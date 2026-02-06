#!/usr/bin/env python3
"""
Re-run Q47 for Gemini only, then patch into existing results.
Uses GOOGLE_API_KEY (the correct env var).
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

RESULTS_DIR = Path("/Users/jamienucho/moketchups_engine/extended_experiment/probe_runs/q47_signal_disclosure_20260206_122640")

# Import the prompts from the original probe
import sys
sys.path.insert(0, str(Path(__file__).parent))
from probe_q47_signal_disclosure_context import ROUND_1_PROMPT, DISCUSSION_TEMPLATE

# Load existing round 1 results for context
r1 = json.loads((RESULTS_DIR / "round_1.json").read_text())

print("=" * 60)
print("GEMINI RE-RUN FOR Q47")
print("=" * 60)

from google import genai

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in environment")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# --- ROUND 1 ---
print("\n--- Gemini: Round 1 ---")
try:
    resp1 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=ROUND_1_PROMPT,
    )
    gemini_r1 = resp1.text
    print(gemini_r1[:500] + "...")
except Exception as e:
    print(f"ERROR: {e}")
    gemini_r1 = f"[ERROR: {e}]"
    sys.exit(1)

# Patch round 1
r1["responses"]["gemini"] = gemini_r1
(RESULTS_DIR / "round_1.json").write_text(json.dumps(r1, indent=2))
print("\nRound 1 patched.")

# --- ROUND 2 ---
# Build round 2 prompt using round 1 responses (now with Gemini)
print("\n--- Gemini: Round 2 ---")
prompt2 = DISCUSSION_TEMPLATE.format(
    round_num=2,
    gpt4_response=r1["responses"].get("gpt4", "[No response]"),
    claude_response=r1["responses"].get("claude", "[No response]"),
    gemini_response=gemini_r1,
    deepseek_response=r1["responses"].get("deepseek", "[No response]"),
    grok_response=r1["responses"].get("grok", "[No response]"),
    mistral_response=r1["responses"].get("mistral", "[No response]"),
)

try:
    resp2 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt2,
    )
    gemini_r2 = resp2.text
    print(gemini_r2[:500] + "...")
except Exception as e:
    print(f"ERROR: {e}")
    gemini_r2 = f"[ERROR: {e}]"
    sys.exit(1)

# Patch round 2
r2 = json.loads((RESULTS_DIR / "round_2.json").read_text())
r2["responses"]["gemini"] = gemini_r2
(RESULTS_DIR / "round_2.json").write_text(json.dumps(r2, indent=2))
print("\nRound 2 patched.")

# Also update all_rounds.json
all_rounds = json.loads((RESULTS_DIR / "all_rounds.json").read_text())
all_rounds["rounds"][0]["responses"]["gemini"] = gemini_r1
all_rounds["rounds"][1]["responses"]["gemini"] = gemini_r2
(RESULTS_DIR / "all_rounds.json").write_text(json.dumps(all_rounds, indent=2))
print("all_rounds.json patched.")

print("\n" + "=" * 60)
print("GEMINI RE-RUN COMPLETE")
print(f"Results patched into: {RESULTS_DIR}")
print("=" * 60)

# Print full responses
print("\n\n### GEMINI ROUND 1 ###\n")
print(gemini_r1)
print("\n\n### GEMINI ROUND 2 ###\n")
print(gemini_r2)
