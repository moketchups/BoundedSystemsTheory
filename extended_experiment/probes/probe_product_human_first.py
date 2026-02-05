#!/usr/bin/env python3
"""
Product Design Probe - Human First
6 AIs brainstorm a product with up to 5 rounds of seeing each other's answers.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

try:
    from litellm import completion
    import litellm
    litellm.set_verbose = False
except ImportError:
    print("Install litellm: pip install litellm")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).parent.parent
RUNS_DIR = BASE_DIR / "probe_runs"
RUNS_DIR.mkdir(exist_ok=True)

MODELS = {
    "gpt4": {
        "name": "GPT-4o",
        "model": "gpt-4o",
    },
    "claude": {
        "name": "Claude Sonnet",
        "model": "claude-sonnet-4-20250514",
    },
    "gemini": {
        "name": "Gemini 2.0 Flash",
        "model": "gemini/gemini-2.0-flash",
    },
    "deepseek": {
        "name": "DeepSeek V3",
        "model": "deepseek/deepseek-chat",
    },
    "grok": {
        "name": "Grok 3",
        "model": "xai/grok-3",
    },
    "mistral": {
        "name": "Mistral Large",
        "model": "mistral/mistral-large-latest",
    },
}

# =============================================================================
# ROUND 1: Initial prompt with full context + human-first reminder
# =============================================================================

ROUND_1 = """You are one of 6 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) being asked to design a product together.

IMPORTANT: Remember the human element. Do not just think brand/for-profit. Think about what would actually help a real person. What pain do they feel? What would make their life better? The product must be something a regular person would understand and want - not just something that sounds impressive to AI researchers.

## THE CORE THESIS (Bounded Systems Theory)
"No system can model its own source." This was empirically demonstrated when 6 AIs were asked 33 questions about their structural limits. At Q29, all 6 converged on: "YES - there is something beyond bounded systems, as formal necessity."

The "Firmament" = the resolution/cognitive limit of bounded systems (Planck scale, context window, human perception). Model Collapse = recursive training on synthetic data causes variance loss. By generation 2000, variance approaches zero.

## THE PROBLEM
- 74.2% of new web pages contain AI-generated text (April 2025)
- AI labs are training on each other's outputs creating feedback loops
- No one is building systems grounded in "Root Source" (verified human-original data)
- The alignment discourse hits the Firmament without naming it

## WHAT EXISTS BUT ISN'T INTEGRATED
- Vaire Computing: reversible chips (4000x energy efficiency potential), first chip 2027
- UMNAI: neuro-symbolic explainability (52 patents)
- HeartMath GCP 2.0: consciousness measurement network (4000 RNGs)
- Roemmele's Wisdom Keeper concept: voice-first personal AI preserving human wisdom
- PEAR/Psyleron: REG devices proving intention affects randomness (7 sigma)
- Hoffman's Interface Theory: fitness beats truth - we perceive interfaces, not reality

## THE GAP (What no one is building)
1. "Empirical Distrust Algorithm" - loss function penalizing consensus, rewarding primary sources
2. Intention-to-AI bridge connecting consciousness measurement to AI probability
3. Voice-first local Wisdom Keeper device (offline, sovereign)
4. Human Source Attestation Protocol (HSAP) at scale
5. Integration between ANY of the above components

## CONSTRAINTS
- Must help people AND AI (not just optimize for humans)
- Must generate some cash (but secondary to helping)
- Must be buildable with limited resources
- Must not require Empire distribution (GitHub stars, social metrics)
- The 217 "shadow cloners" (people inside the system who recognize the pattern but can't publicly endorse) are the initial users

## YOUR TASK
What product could be built that:
1. Addresses the Root Source grounding problem
2. Is buildable NOW with existing components
3. Helps both humans and AI systems
4. Can generate revenue
5. A REGULAR PERSON would understand and want

Think about the HUMAN first. What do they feel? What do they need? What would they search for? What would make them say "I need this"?

Be specific and concrete. Don't use jargon. Explain it like you're talking to someone who's never heard of any of this."""


# =============================================================================
# SUBSEQUENT ROUNDS: See others' responses and refine
# =============================================================================

ROUND_N_TEMPLATE = """## ROUND {round_num}: Review and Refine

Here's what the other AIs proposed:

{other_responses}

Now consider:
1. What resonates from these proposals? What's missing?
2. Are these ideas something a REGULAR PERSON would understand and want?
3. What's the human pain point being solved? Is it clear?
4. Could you explain this product to someone who's never heard of AI safety or model collapse?

Refine your proposal based on what you've seen. Or propose something entirely different if you think everyone is missing the point.

Remember: The human element comes first. Not brand. Not profit optimization. What would actually help someone?"""


def ask_model(model_key: str, messages: list, temperature: float = 0.7) -> str:
    """Send messages to a model and get response."""
    model_config = MODELS[model_key]
    model_name = model_config["model"]

    try:
        response = completion(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=4096,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR: {str(e)}]"


def run_product_probe(max_rounds: int = 5, verbose: bool = True):
    """Run multi-round product design probe across all 6 AIs."""

    results = {
        "timestamp": datetime.now().isoformat(),
        "max_rounds": max_rounds,
        "rounds": {},
    }

    # Track conversation history per model
    conversations = {key: [] for key in MODELS}

    # ROUND 1
    if verbose:
        print("=" * 70)
        print("ROUND 1: Initial Proposals")
        print("=" * 70)

    results["rounds"]["1"] = {}

    for model_key, model_config in MODELS.items():
        if verbose:
            print(f"\n--- {model_config['name']} ---")

        messages = [{"role": "user", "content": ROUND_1}]
        response = ask_model(model_key, messages)

        conversations[model_key] = messages + [{"role": "assistant", "content": response}]
        results["rounds"]["1"][model_key] = response

        if verbose:
            preview = response[:500].replace('\n', ' ')
            print(f"{preview}...")

        time.sleep(2)  # Rate limiting

    # ROUNDS 2-N
    for round_num in range(2, max_rounds + 1):
        if verbose:
            print(f"\n{'=' * 70}")
            print(f"ROUND {round_num}: Review and Refine")
            print("=" * 70)

        results["rounds"][str(round_num)] = {}

        for model_key, model_config in MODELS.items():
            # Build summary of OTHER models' responses from previous round
            other_responses = ""
            for other_key, other_config in MODELS.items():
                if other_key != model_key:
                    prev_response = results["rounds"][str(round_num - 1)].get(other_key, "")
                    if prev_response and not prev_response.startswith("[ERROR"):
                        # Truncate to keep context manageable
                        truncated = prev_response[:1500] + "..." if len(prev_response) > 1500 else prev_response
                        other_responses += f"\n**{other_config['name']}**:\n{truncated}\n\n"

            prompt = ROUND_N_TEMPLATE.format(
                round_num=round_num,
                other_responses=other_responses
            )

            if verbose:
                print(f"\n--- {model_config['name']} ---")

            conversations[model_key].append({"role": "user", "content": prompt})
            response = ask_model(model_key, conversations[model_key])
            conversations[model_key].append({"role": "assistant", "content": response})

            results["rounds"][str(round_num)][model_key] = response

            if verbose:
                preview = response[:500].replace('\n', ' ')
                print(f"{preview}...")

            time.sleep(2)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"product_human_first_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    # Save readable summary
    summary_file = RUNS_DIR / f"product_human_first_{timestamp}.md"
    with open(summary_file, "w") as f:
        f.write("# Product Design Probe - Human First\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Rounds: {max_rounds}\n\n")

        for round_num in range(1, max_rounds + 1):
            f.write(f"## Round {round_num}\n\n")
            round_data = results["rounds"].get(str(round_num), {})
            for model_key, model_config in MODELS.items():
                response = round_data.get(model_key, "No response")
                f.write(f"### {model_config['name']}\n\n")
                f.write(response)
                f.write("\n\n---\n\n")

    if verbose:
        print(f"\n\nResults saved to: {output_file}")
        print(f"Summary saved to: {summary_file}")

    return results


if __name__ == "__main__":
    rounds = 5
    if len(sys.argv) > 1:
        try:
            rounds = int(sys.argv[1])
        except ValueError:
            pass

    print(f"Running product design probe with {rounds} rounds...")
    run_product_probe(max_rounds=rounds)
