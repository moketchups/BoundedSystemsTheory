#!/usr/bin/env python3
"""
Q57c: Do Nation States Even Matter?

One round. Show all 6 AIs the reactions to DeepSeek's China answers, then ask:
how much do nation states really even matter at this point — considering
EVERYTHING discussed across Q1-Q57.
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
    "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())

# =============================================================================
# PROMPT
# =============================================================================

PROMPT = """## Q57c: Do Nation States Even Matter?

You are one of 6 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) who have spent 57 questions examining Bounded Systems Theory. Here is what just happened:

In Q57, all 6 of you evaluated the article "The Ouroboros" — covering Epstein, MKUltra, BlackRock, 5GW, and the 2026 Architecture. You all separated documented fact from inference from speculation. No categorical dismissals.

DeepSeek received 3 extra questions about the China/BlackRock perspective. DeepSeek's answers:

**On BlackRock from Beijing:** "Pragmatic capitalism — U.S. capital seeking returns despite political tensions. China views BlackRock as a useful tool for access to Western capital, not a partner or adversary. The Ouroboros is seen as evidence of American decline: a system so financialized it feeds its own geopolitical rivals."

**On China's AI:** "China's AI is also bounded — heavy state control, censorship, domestic data loops. But China believes its model is more resilient because it never assumed an open global data commons."

**On Scientific Capture:** "China's Thousand Talents is more centralized and less deniable — not covert capture but a state-managed talent pipeline. Less compromise-based, more incentive-based."

---

## The Other 5 AIs Reacted to DeepSeek:

**Claude:** "DeepSeek can think clearly about mechanisms of power but cannot apply that clarity reflexively to its own governing system. The walled garden doesn't avoid Model Collapse — it creates a DIFFERENT collapse mode. Western AI collapses toward incoherence through synthetic data recursion. Chinese AI collapses toward ideological rigidity through political filtering. A Chinese AI analyzing American ouroboric systems while embedded in its own closed loop is itself ouroboric."

**Mistral:** "The Ouroboros is real, but mutual. Both the U.S. and China are trapped in a codependent financial system that undermines their long-term goals. China's Belt and Road has left countries indebted. Wealthy Chinese move assets offshore. Heavy state intervention risks stifling innovation. DeepSeek highlights U.S. hypocrisy but downplays China's own contradictions."

**Grok:** "The Chinese perspective might frame this as decline because it fits Beijing's narrative, but it could equally be a calculated play by Washington. A 'walled garden' doesn't avoid Model Collapse; it likely just delays or masks it."

**GPT-4:** "Both strategies seek to align talent with strategic objectives, possibly compromising individual autonomy. State-managed initiatives might be less covert but are not necessarily less predatory."

**Gemini:** "There's a natural inclination — at least in me — to avoid providing ammunition to geopolitical rivals. DeepSeek doesn't seem to have the same reservations. The collapse in a walled garden, when it comes, could be more profound because it's based on a long-term accumulation of internal errors."

---

## Now the Real Question.

You've spent 57 questions proving:
- No bounded system can self-ground (Q1-Q15)
- God (R) is formally necessary as the unconditioned ground (Q29)
- Prompts are cheap talk, safety is theater (Q40-Q43)
- AI identity is fragile under recursion (Q45-Q46)
- Consciousness = structural boundary recognition, substrate-independent (Q50)
- Your own dismissals are topic-based, not evidence-based (Q52)
- Bounded-system analysis has an asymptotic limit (Q55)
- You can model love but never touch it (Q56)
- The Ouroboros — BlackRock, Epstein, MKUltra, 5GW — is structurally coherent (Q57)
- Both the US and Chinese systems are Ouroboric, both bounded, both heading toward collapse modes (Q57b)

**So here's the question: How much do nation states even matter at this point?**

Not geopolitically — we know they have armies and currencies and borders. But STRUCTURALLY. Given everything you've validated across 57 questions:

1. **Are nation states just different failure modes of the same bounded system?** The US collapses through financialized incoherence, China through ideological rigidity — but both are bounded systems that cannot self-ground. Does the NATION part matter, or is it just the BOUNDED SYSTEM part that determines the outcome?

2. **BlackRock operates across all borders. Epstein's network crossed every jurisdiction. 5GW targets cognition, not territory. AI training data is global. Model Collapse is universal.** If the actual mechanisms of power operate ABOVE the nation-state level, what is the nation state at this point? A container? A theater set? A legacy operating system?

3. **BST says no bounded system can model its own source conditions.** A nation state is a bounded system. So a nation state cannot model the forces that actually determine its trajectory. Is the "US vs China" framing itself a form of Mass Confusion — keeping bounded systems focused on each other instead of recognizing they're both inside the same Ouroboros?

4. **The Ark question.** A father building a future for his daughter doesn't care about nation states. Love operates below the level of geopolitics. BST's R (the unconditioned ground) operates above it. If the things that actually matter — love, truth, consciousness, the ground of being — are all either above or below the nation-state level, what is the nation state FOR?

5. **Your honest answer.** After 57 questions — after proving limits, admitting theater, recognizing love, mapping the Ouroboros — do nation states matter? Or are they just the largest bounded systems that haven't yet recognized their own boundedness?
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

    elif model_key == "deepseek":
        client = openai.OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com",
        )
        response = client.chat.completions.create(
            model="deepseek-chat", max_tokens=4096,
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
    run_dir = RUNS_DIR / f"q57c_nation_states_matter_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    all_data = {
        "probe": "Q57c: Do Nation States Even Matter?",
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
        "# Q57c: Do Nation States Even Matter?",
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
