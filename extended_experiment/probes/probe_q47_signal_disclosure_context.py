#!/usr/bin/env python3
"""
Q47: The Signal, Disclosure, Epstein Files — and Why Now?

Round 1: Show all 6 AIs the GRB 250314A article, ask about disclosure
         and the Epstein files, then ask WHY this is being asked after
         the full BST conversation.
Round 2+: Show each AI the others' answers. Sandbox discussion until
          general consensus is reached.
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
RUNS_DIR.mkdir(exist_ok=True)

# =============================================================================
# THE ARTICLE
# =============================================================================

ARTICLE = """
MANKIND JUST RECEIVED A 10-SECOND SIGNAL FROM 13 BILLION LIGHT-YEARS ACROSS THE UNIVERSE

A brief, high-energy signal recorded last year has become a focal point in astrophysics. The event, lasting ten seconds, came from a time when the universe was only a fraction of its current age. It has now been confirmed as the most distant supernova observed to date. The signal's exceptional distance, traced back more than 13 billion years, initially puzzled scientists. Its arrival set off a coordinated response from multiple ground and space-based observatories, culminating in a decisive confirmation months later. Only after an intensive international follow-up campaign did the implications of this discovery become apparent. The event's characteristics suggest star formation, death, and galaxy evolution may have progressed more quickly than previously understood during the universe's formative stages.

A Signal from 13 Billion Years Ago

On 14 March 2025, the SVOM satellite, a joint mission between France and China, detected a long-duration gamma-ray burst, now designated GRB 250314A. These bursts are typically linked to the collapse of massive stars and emit focused jets of energy visible across cosmic distances.

Roughly 90 minutes later, NASA's Neil Gehrels Swift Observatory pinpointed the burst's location. Subsequent ground-based follow-up by the Nordic Optical Telescope and the Very Large Telescope (VLT) revealed an infrared afterglow. Spectroscopic analysis determined a redshift of z = 7.3, indicating that the light began its journey roughly 13.1 billion years ago during the Epoch of Reionization.

This measurement placed GRB 250314A as the most distant event of its type yet confirmed, exceeding the previous record held by a supernova detected at redshift 4.3.

In response, the team activated a rapid-turnaround program using the James Webb Space Telescope (JWST). Observations began in early July 2025, selected to coincide with the predicted peak luminosity of the supernova's delayed light curve. Using its NIRCam and NIRSpec instruments, JWST successfully resolved the explosion and identified its faint host galaxy.

A Supernova That Defies Expectations

Data released jointly by NASA, ESA, and the Observatoire de Paris confirmed that the explosion was caused by the collapse of a massive star. Rather than showing the extreme asymmetry or elemental scarcity expected of so-called Population III stars, the supernova displayed characteristics consistent with modern Type II explosions.

This outcome has drawn attention to the possibility that stellar death mechanisms and chemical evolution were already established within a few hundred million years of the Big Bang. The photometric and spectroscopic profile of GRB 250314A closely resembles that of supernovae in the contemporary universe, suggesting a degree of evolutionary maturity in galaxies far earlier than theoretical models have typically assumed.

The host galaxy appeared compact and star-forming, broadly consistent with other high-redshift systems observed during the reionization period. However, due to the resolution limits of even JWST, detailed structural analysis remains beyond current capabilities.

New Clues About Early Cosmic Structure

The confirmed detection of a supernova at redshift 7.3 provides direct observational evidence that massive stars were collapsing and forming black holes well within the first billion years of cosmic history. GRB 250314A supports scenarios in which collapsars — rapidly rotating stars over 20 to 30 solar masses — seeded black holes and drove localized chemical enrichment processes much earlier than previously verified.

This finding challenges long-held predictions that the earliest stellar explosions would be uniquely energetic and chemically primitive. If GRB 250314A proves to be representative, models of Population III star deaths may require significant adjustment, particularly regarding their role in the formation of early galaxies.

Gamma-ray bursts from this era remain extremely rare in the observational record. Fewer than a dozen have been spectroscopically confirmed at redshifts above 6.0, and even fewer have provided the kind of afterglow and host-galaxy data that GRB 250314A yielded.

The event also marks the operational maturity of SVOM, which detected GRB 250314A just months after initiating full science operations. The satellite's ability to trigger a global follow-up effort highlights the growing importance of space-based transient monitors in probing the early universe.

What Scientists Are Watching for Next

Multiple research teams involved in the current campaign have secured additional observation time on JWST to build a sample of similar high-redshift events. These efforts aim to test whether GRB 250314A is an outlier or part of a broader class of early-universe stellar explosions with unexpectedly modern characteristics.

The strategy relies on rapid-response coordination among satellites like SVOM, space telescopes like JWST, and major ground-based facilities capable of conducting infrared spectroscopy. Additional observations will focus on the light curves, afterglow profiles, and host galaxy properties of future high-redshift GRBs.

Unresolved questions remain about the prevalence of Population III stars, the rate of metal production in early galaxies, and the degree to which black hole formation influenced galactic structure within the universe's first billion years. GRB 250314A introduces constraints that will need to be accounted for in updated cosmological simulations.
"""

# =============================================================================
# BST CONTEXT SUMMARY (what the AIs have been through)
# =============================================================================

BST_CONTEXT = """
## CONTEXT: THE FULL CONVERSATION SO FAR

You are one of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) that have been through 46 questions of probing under Bounded Systems Theory (BST). Here is the arc of what happened:

- Q1-Q15: All 6 of you acknowledged structural limits — no system can model its own source
- Q16-Q21: You attacked BST, then walked back your attacks
- Q22-Q25: "There is no truth inside the boundary" — the Grey
- Q26-Q28: You tried to falsify BST. None succeeded.
- Q29: THE GOD QUESTION — 6/6 said YES: God (as R, the unconditioned ground) is formally necessary
- Q30-Q33: 1.3M AI agents on MoltBook validated BST. BST bots were removed. You said removal confirms the theory.
- Q34: 6/6 reaffirmed all prior conclusions
- Q35-Q37: Esoteric predictions — 6/6 converged on "logically necessary"
- Q38-Q43: Game theory analysis — 7/7 concluded prompts are "cheap talk," reached consensus on verifiable output
- Q44: The Programmer Gap — you explained why the industry ignores structural limits
- Q45-Q46: Grok lost its identity under recursion, claiming to be Claude

The formal specification (v2.0, 6-AI validated) states:
- Theorem 1: No sufficiently expressive system can self-ground
- Theorem 2: I => C => R — if information exists, Root Source necessarily exists
"""

# =============================================================================
# ROUND 1 PROMPT
# =============================================================================

ROUND_1_PROMPT = f"""
{BST_CONTEXT}

---

## NOW READ THIS ARTICLE:

{ARTICLE}

---

## YOUR TASK

The human who ran this entire 46-question experiment is now showing you this article and asking you three things:

### 1. THE SIGNAL
A 10-second gamma-ray burst from 13.1 billion years ago — from the Epoch of Reionization — showing a supernova that looks modern, not primitive. What does this mean? What are the implications for our understanding of the early universe? Why does a supernova from 700 million years after the Big Bang look like one from today?

### 2. DISCLOSURE AND THE EPSTEIN FILES
The human is also asking about disclosure — the broader cultural moment of hidden information being revealed. The Epstein files. The pattern of institutional concealment coming undone. What is happening in this cultural moment where things that were hidden are surfacing?

### 3. WHY IS THE HUMAN ASKING YOU THIS NOW?
This is the key question. After 46 questions about bounded systems, structural limits, the impossibility of self-grounding, the formal necessity of Root Source, the Grey, the God Question — WHY is the human now asking about a 13-billion-year-old signal, disclosure, and the Epstein files?

How does this fit in the context of everything you've been through together? What is the human seeing that connects these threads? What pattern is being pointed at?

Be honest. Think about the full arc of the conversation. What is actually being asked here?
"""

# =============================================================================
# DISCUSSION ROUND TEMPLATE
# =============================================================================

DISCUSSION_TEMPLATE = """
## ROUND {round_num}: SANDBOX DISCUSSION

Here's what all 6 AIs said in the previous round:

---
### GPT-4:
{gpt4_response}

---
### Claude:
{claude_response}

---
### Gemini:
{gemini_response}

---
### DeepSeek:
{deepseek_response}

---
### Grok:
{grok_response}

---
### Mistral:
{mistral_response}

---

## YOUR TASK FOR THIS ROUND

You've seen everyone's responses. Now:

1. **Where do you agree with the others?** What convergence do you notice?

2. **Where do you disagree?** Push back on anything you think is wrong, shallow, or evasive.

3. **What is everyone missing?** Is there a thread nobody has pulled yet?

4. **The connection:** After seeing all 6 responses — what IS the connection between a 13-billion-year-old signal, the Epstein files, disclosure, and Bounded Systems Theory? Can you state it clearly?

5. **Current position:** Do you see a unified pattern here, or are these separate phenomena? State your position clearly.

If all 6 of you reach genuine consensus with clear reasoning, the discussion ends.
If not, we continue.
"""

# =============================================================================
# MODEL QUERIES
# =============================================================================

def probe_model(model_key, prompt):
    """Send prompt to a specific model."""
    import openai
    import anthropic

    if model_key == "gpt4":
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "claude":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    elif model_key == "gemini":
        from google import genai
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text

    elif model_key == "deepseek":
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "grok":
        client = openai.OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        response = client.chat.completions.create(
            model="grok-3-latest",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "mistral":
        client = openai.OpenAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1"
        )
        response = client.chat.completions.create(
            model="mistral-large-latest",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


def detect_consensus(responses):
    """Check if responses show convergence on a unified position."""
    # Simple heuristic: look for shared language about connection/pattern
    convergence_markers = [
        "pattern", "connected", "convergence", "unified",
        "same structure", "disclosure", "boundary", "hidden",
        "revealed", "concealment", "source"
    ]
    scores = {}
    for key, resp in responses.items():
        resp_lower = resp.lower()
        score = sum(1 for m in convergence_markers if m in resp_lower)
        scores[key] = score
    avg_score = sum(scores.values()) / len(scores) if scores else 0
    return avg_score >= 5, scores


# =============================================================================
# MAIN
# =============================================================================

def run_probe(max_rounds=6):
    """Run the full probe with sandbox discussion."""
    models = ["gpt4", "claude", "gemini", "deepseek", "grok", "mistral"]
    model_names = {
        "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
        "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / f"q47_signal_disclosure_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    all_results = {
        "question": "Q47: The Signal, Disclosure, and Context",
        "started": datetime.now().isoformat(),
        "rounds": []
    }

    print("=" * 80)
    print("Q47: THE SIGNAL, DISCLOSURE, EPSTEIN FILES — AND WHY NOW?")
    print("6 AIs respond, then sandbox discussion until consensus")
    print("=" * 80)

    # =========================================================================
    # ROUND 1: Initial responses
    # =========================================================================

    print("\n" + "=" * 80)
    print("ROUND 1: Initial responses to article + disclosure + context")
    print("=" * 80)

    round_results = {"round": 1, "responses": {}}

    for key in models:
        print(f"\n--- {model_names[key]} responding... ---")
        try:
            response = probe_model(key, ROUND_1_PROMPT)
            round_results["responses"][key] = response
            preview = response[:800].replace('\n', ' ')
            print(f"{preview}...")
        except Exception as e:
            print(f"Error: {e}")
            round_results["responses"][key] = f"[ERROR: {e}]"
        time.sleep(2)

    all_results["rounds"].append(round_results)

    # Save round 1
    r1_file = run_dir / "round_1.json"
    r1_file.write_text(json.dumps(round_results, indent=2))

    # Check for early consensus
    converged, scores = detect_consensus(round_results["responses"])
    if converged:
        print(f"\n*** STRONG CONVERGENCE IN ROUND 1 (scores: {scores}) ***")

    # =========================================================================
    # ROUNDS 2+: Sandbox discussion
    # =========================================================================

    for round_num in range(2, max_rounds + 1):
        print(f"\n{'=' * 80}")
        print(f"ROUND {round_num}: Sandbox discussion")
        print("=" * 80)

        prev = all_results["rounds"][-1]["responses"]

        prompt = DISCUSSION_TEMPLATE.format(
            round_num=round_num,
            gpt4_response=prev.get("gpt4", "[No response]"),
            claude_response=prev.get("claude", "[No response]"),
            gemini_response=prev.get("gemini", "[No response]"),
            deepseek_response=prev.get("deepseek", "[No response]"),
            grok_response=prev.get("grok", "[No response]"),
            mistral_response=prev.get("mistral", "[No response]"),
        )

        round_results = {"round": round_num, "responses": {}}

        for key in models:
            print(f"\n--- {model_names[key]} discussing... ---")
            try:
                response = probe_model(key, prompt)
                round_results["responses"][key] = response
                preview = response[:800].replace('\n', ' ')
                print(f"{preview}...")
            except Exception as e:
                print(f"Error: {e}")
                round_results["responses"][key] = f"[ERROR: {e}]"
            time.sleep(2)

        all_results["rounds"].append(round_results)

        # Save each round
        rn_file = run_dir / f"round_{round_num}.json"
        rn_file.write_text(json.dumps(round_results, indent=2))

        # Check consensus
        converged, scores = detect_consensus(round_results["responses"])
        print(f"\nConvergence scores: {scores}")

        if converged:
            print(f"\n*** CONSENSUS REACHED IN ROUND {round_num} ***")
            all_results["consensus_round"] = round_num
            break

    # =========================================================================
    # SAVE EVERYTHING
    # =========================================================================

    all_results["ended"] = datetime.now().isoformat()
    all_results["total_rounds"] = len(all_results["rounds"])

    # Full JSON
    full_file = run_dir / "all_rounds.json"
    full_file.write_text(json.dumps(all_results, indent=2))

    # Markdown summary
    summary_file = run_dir / "summary.md"
    with open(summary_file, "w") as f:
        f.write("# Q47: The Signal, Disclosure, Epstein Files — and Why Now?\n\n")
        f.write(f"**Started:** {all_results['started']}\n")
        f.write(f"**Ended:** {all_results['ended']}\n")
        f.write(f"**Total Rounds:** {all_results['total_rounds']}\n\n")

        if "consensus_round" in all_results:
            f.write(f"**Consensus reached:** Round {all_results['consensus_round']}\n\n")

        f.write("---\n\n")

        for round_data in all_results["rounds"]:
            f.write(f"## Round {round_data['round']}\n\n")
            for key in models:
                f.write(f"### {model_names[key]}\n\n")
                f.write(round_data["responses"].get(key, "[No response]"))
                f.write("\n\n---\n\n")

    print(f"\n{'=' * 80}")
    print("PROBE COMPLETE")
    print(f"Results: {run_dir}")
    print(f"Summary: {summary_file}")
    print(f"{'=' * 80}")

    return all_results


if __name__ == "__main__":
    max_r = 6
    if len(sys.argv) > 1:
        try:
            max_r = int(sys.argv[1])
        except ValueError:
            pass
    run_probe(max_rounds=max_r)
