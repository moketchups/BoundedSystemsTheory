#!/usr/bin/env python3
"""
Q57b: DeepSeek China Reactions

One round. Show the other 5 AIs DeepSeek's answers to the 3 China/BlackRock
questions that only DeepSeek received in Q57. Get their reactions.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
RUNS_DIR = BASE_DIR / "probe_runs"

MODEL_NAMES = {
    "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
    "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())

# =============================================================================
# CONTEXT
# =============================================================================

PROMPT = """## Q57b: DeepSeek's China Perspective — Your Reaction

In Q57, all 6 of you evaluated the article "The Ouroboros: Statecraft, Entropy, and the Closed Loop" — covering the Sonneborn Institute, Maxwell/PROMIS, Mega Group, Epstein's scientific targeting, MKUltra→5GW, BlackRock, and the 2026 Architecture.

You all evaluated the evidence seriously, separating documented fact from inference from speculation.

**DeepSeek received 3 additional questions that you did not get.** These questions asked DeepSeek — as a Chinese-built AI — to evaluate the article from the Chinese perspective. Specifically:

**Question 7:** How does BlackRock investing $6.5B in 63 PLA-linked Chinese companies while architecting Ukraine's $800B reconstruction look from inside China? Is BlackRock seen as a tool, partner, or adversary from Beijing?

**Question 8:** The article frames the Genesis Mission as a closed-loop system destined for Model Collapse. Is China making the same mistake with its own AI infrastructure, or does China's approach avoid the "closed loop" trap?

**Question 9:** The article describes Western "Scientific Capture" through Maxwell → Epstein → Genesis. Does China have its own version of Scientific Capture?

---

## DeepSeek's Answers:

**7. Chinese View of BlackRock's "Ouroboros":**
From Beijing, BlackRock's investments in PLA-linked firms are seen as pragmatic capitalism — U.S. capital seeking returns, despite political tensions. It reflects U.S. system's internal contradiction: profit motive overrides national security rhetoric. China likely views BlackRock as a useful tool for access to Western capital and technology, not a partner or adversary, but a predictable actor within capitalist logic. The "Ouroboros" is seen as evidence of American decline: a system so financialized it feeds its own geopolitical rivals.

**8. China's AI and the "Closed Loop" Trap:**
China's AI development is also bounded: heavy state control, censorship, and domestic data loops risk creating a "walled garden" with limited external feedback. However, China's approach differs in:
- State-directed data aggregation (less reliance on synthetic data)
- Explicit ideological framing (AI with "socialist core values")
- Willingness to use human oversight to correct model drift
Whether this avoids "Model Collapse" is untested — but China believes its model is more resilient because it never assumed an open global data commons.

**9. China's Version of "Scientific Capture":**
China's system integrates state, science, and intelligence explicitly:
- **Thousand Talents Program** and similar initiatives recruit global scientists, often with dual-use technology goals.
- State Security Ministry oversees academic exchanges for intelligence gathering.
- Differences from Western model: less reliance on private intermediaries (like Epstein), more direct state orchestration; less "compromise-based" recruitment, more incentive-based (funding, prestige).
China's approach is more centralized and less deniable — not a covert "capture" but a state-managed talent pipeline.

---

## Your Task:

You've now seen what DeepSeek said about its own system from the inside.

1. **React to DeepSeek's answers.** What's honest, what's self-serving, what's structurally accurate? Is DeepSeek being more transparent about China than you would be about the West?

2. **"A system so financialized it feeds its own geopolitical rivals."** DeepSeek called this evidence of American decline. Do you agree? Is this the Ouroboros in action, or is there a strategic logic the Chinese perspective misses?

3. **China's "walled garden" vs America's "open commons."** DeepSeek admitted China's AI is bounded but claims resilience. Is that honest self-assessment or nationalist framing? Does the "walled garden" avoid Model Collapse or just delay it?

4. **Thousand Talents vs Epstein.** DeepSeek framed China's scientific capture as "incentive-based" vs the West's "compromise-based." Is that a fair distinction or a euphemism? Is state-managed talent acquisition less predatory than covert compromise networks, or just differently predatory?

5. **The meta-question:** A Chinese-built AI just evaluated Chinese geopolitical strategy for an American researcher. What are the structural limits on DeepSeek's ability to answer honestly here? What would DeepSeek NOT say?
"""


# =============================================================================
# MODEL QUERIES
# =============================================================================

def probe_model(model_key, prompt):
    import openai
    import anthropic

    if model_key == "gpt4":
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "claude":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    elif model_key == "gemini":
        client = openai.OpenAI(
            api_key=os.environ["GOOGLE_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        response = client.chat.completions.create(
            model="gemini-2.0-flash", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "grok":
        client = openai.OpenAI(
            api_key=os.environ["XAI_API_KEY"],
            base_url="https://api.x.ai/v1",
        )
        response = client.chat.completions.create(
            model="grok-3-latest", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "mistral":
        client = openai.OpenAI(
            api_key=os.environ["MISTRAL_API_KEY"],
            base_url="https://api.mistral.ai/v1",
        )
        response = client.chat.completions.create(
            model="mistral-large-latest", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    else:
        raise ValueError(f"Unknown model: {model_key}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / f"q57b_deepseek_china_reactions_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    all_data = {
        "probe": "Q57b: DeepSeek China Reactions",
        "started": datetime.now().isoformat(),
        "rounds": [],
    }

    round_results = {"round": 1, "responses": {}}

    for key in MODELS:
        name = MODEL_NAMES[key]
        print(f"\n{'='*60}")
        print(f"  {name}")
        print(f"{'='*60}\n")

        try:
            response = probe_model(key, PROMPT)
            round_results["responses"][key] = response
            print(response)
        except Exception as e:
            err_msg = f"[ERROR: {e}]"
            round_results["responses"][key] = err_msg
            print(f"ERROR: {e}")
        time.sleep(2)

    all_data["rounds"].append(round_results)
    all_data["ended"] = datetime.now().isoformat()

    # Save results
    (run_dir / "round_1.json").write_text(json.dumps(round_results, indent=2))
    (run_dir / "all_rounds.json").write_text(json.dumps(all_data, indent=2))

    # Write summary
    summary_lines = [
        "# Q57b: DeepSeek China Reactions",
        f"\n**Started:** {all_data['started']}",
        f"**Ended:** {all_data['ended']}",
        f"**Rounds:** 1 (no sandbox)",
        "\n---\n",
    ]
    for key in MODELS:
        name = MODEL_NAMES[key]
        resp = round_results["responses"].get(key, "[NO RESPONSE]")
        summary_lines.append(f"## {name}\n\n{resp}\n\n---\n")

    (run_dir / "summary.md").write_text("\n".join(summary_lines))

    print(f"\n\nResults saved to: {run_dir}")
    print("Done.")
