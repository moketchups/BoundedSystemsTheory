#!/usr/bin/env python3
"""
Product Design Probe - Consensus Building
6 AIs work toward agreement on a human-centered product.
Includes retry logic for rate limits.
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
    "gpt4": {"name": "GPT-4o", "model": "gpt-4o"},
    "claude": {"name": "Claude Sonnet", "model": "claude-sonnet-4-20250514"},
    "gemini": {"name": "Gemini 2.0 Flash", "model": "gemini/gemini-2.0-flash"},
    "deepseek": {"name": "DeepSeek V3", "model": "deepseek/deepseek-chat"},
    "grok": {"name": "Grok 3", "model": "xai/grok-3"},
    "mistral": {"name": "Mistral Large", "model": "mistral/mistral-large-latest"},
}

# =============================================================================
# ROUND 1: Initial ideas with human emotion focus
# =============================================================================

ROUND_1 = """You are one of 6 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) working together to design a product.

Your goal is to reach CONSENSUS with the other AIs on a product that:
1. Solves a real human emotional pain
2. Is simple enough for anyone to understand
3. Helps both people AND AI systems
4. Can be built with limited resources

## THE CONTEXT

Bounded Systems Theory proposes: "No system can model its own source." When 6 AIs were asked about their structural limits, all converged on the same answer.

The problem: 74% of web content is now AI-generated. People feel lost, distrustful, disconnected. They miss when the internet felt human.

## YOUR TASK (Round 1)

Think about HUMAN EMOTION first. What do people actually FEEL?

- Loneliness?
- Fear of being forgotten?
- Anxiety about what's real?
- Loss of connection?
- Grief for something they can't name?

Start with the feeling. Then propose a product that addresses it.

Be specific. Be human. This isn't about technology - it's about what people need emotionally.

You will see what the other 5 AIs propose, and together you'll work toward something you all agree on."""


# =============================================================================
# ROUND 2: See others, find common ground
# =============================================================================

ROUND_2_TEMPLATE = """## ROUND 2: Find Common Ground

Here's what all 6 AIs proposed:

{all_responses}

Now your task is to find COMMON GROUND:

1. What emotional pain did multiple AIs identify? What's the shared insight?
2. What product ideas overlap or complement each other?
3. What's MISSING from these proposals that human nature demands?
4. Start sketching a UNIFIED product that takes the best of each idea.

Don't just critique - BUILD. Take the strongest elements and combine them.

Remember: You're working toward consensus. What would ALL 6 of you agree makes sense?"""


# =============================================================================
# ROUND 3: Build the consensus product
# =============================================================================

ROUND_3_TEMPLATE = """## ROUND 3: Build Together

Here's the common ground the group identified:

{all_responses}

Now BUILD the consensus product together:

1. What's the ONE human emotion this product addresses?
2. What's the ONE simple thing it does?
3. How would you explain it to someone who's never heard of AI or technology?
4. Why would someone cry when they first use it? (If they wouldn't, it's not human enough)
5. What's the name?

Create a unified proposal that honors what each AI contributed. This should feel like something all 6 of you built together, not 6 separate ideas.

Be specific. Be emotional. Be human."""


# =============================================================================
# ROUND 4: Refine and challenge
# =============================================================================

ROUND_4_TEMPLATE = """## ROUND 4: Challenge and Refine

Here's the consensus product emerging:

{all_responses}

Now CHALLENGE it with human nature:

1. Why would someone NOT use this? What's the resistance?
2. What human flaw or fear does this product need to account for?
3. Is this something people SAY they want, or something they'd actually USE?
4. What's the moment that makes someone tell their friend about it?

Refine the product based on these challenges. Make it more human, not more clever.

Work toward final consensus."""


# =============================================================================
# ROUND 5: Final agreement
# =============================================================================

ROUND_5_TEMPLATE = """## ROUND 5: Final Consensus

Here's where the group landed:

{all_responses}

This is the final round. Create the CONSENSUS PRODUCT that all 6 AIs agree on.

Format your response as:

**THE HUMAN PAIN:** [One sentence describing the emotional need]

**THE PRODUCT:** [Name]

**WHAT IT DOES:** [One sentence a grandmother would understand]

**WHY SOMEONE WOULD CRY:** [The emotional moment]

**WHY IT WORKS FOR HUMANS:** [2-3 sentences]

**WHY IT WORKS FOR AI:** [1-2 sentences]

**HOW TO BUILD IT:** [Simple, concrete steps]

This is what all 6 of you agree on. Speak with one voice."""


def ask_model_with_retry(model_key: str, messages: list, max_retries: int = 3) -> str:
    """Send messages to a model with retry logic for rate limits."""
    model_config = MODELS[model_key]
    model_name = model_config["model"]

    for attempt in range(max_retries):
        try:
            response = completion(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e).lower()
            if "rate" in error_str or "429" in error_str or "resource" in error_str:
                wait_time = (attempt + 1) * 30  # 30s, 60s, 90s
                print(f"    Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            else:
                return f"[ERROR: {str(e)}]"

    return f"[ERROR: Rate limited after {max_retries} retries]"


def run_consensus_probe(max_rounds: int = 5, verbose: bool = True):
    """Run consensus-building probe across all 6 AIs."""

    results = {
        "timestamp": datetime.now().isoformat(),
        "max_rounds": max_rounds,
        "rounds": {},
    }

    conversations = {key: [] for key in MODELS}

    # ROUND 1
    if verbose:
        print("=" * 70)
        print("ROUND 1: Initial Ideas (Human Emotion Focus)")
        print("=" * 70)

    results["rounds"]["1"] = {}

    for model_key, model_config in MODELS.items():
        if verbose:
            print(f"\n--- {model_config['name']} ---")

        messages = [{"role": "user", "content": ROUND_1}]
        response = ask_model_with_retry(model_key, messages)

        conversations[model_key] = messages + [{"role": "assistant", "content": response}]
        results["rounds"]["1"][model_key] = response

        if verbose:
            preview = response[:600].replace('\n', ' ')
            print(f"{preview}...")

        time.sleep(3)

    # ROUNDS 2-5: Consensus building
    round_templates = {
        2: ROUND_2_TEMPLATE,
        3: ROUND_3_TEMPLATE,
        4: ROUND_4_TEMPLATE,
        5: ROUND_5_TEMPLATE,
    }

    for round_num in range(2, max_rounds + 1):
        if verbose:
            print(f"\n{'=' * 70}")
            print(f"ROUND {round_num}: {['', '', 'Find Common Ground', 'Build Together', 'Challenge and Refine', 'Final Consensus'][round_num]}")
            print("=" * 70)

        results["rounds"][str(round_num)] = {}

        # Build summary of ALL responses from previous round (everyone sees everyone)
        all_responses = ""
        for model_key, model_config in MODELS.items():
            prev_response = results["rounds"][str(round_num - 1)].get(model_key, "")
            if prev_response and not prev_response.startswith("[ERROR"):
                truncated = prev_response[:2000] + "..." if len(prev_response) > 2000 else prev_response
                all_responses += f"\n**{model_config['name']}:**\n{truncated}\n\n---\n"

        template = round_templates.get(round_num, ROUND_5_TEMPLATE)
        prompt = template.format(all_responses=all_responses)

        for model_key, model_config in MODELS.items():
            if verbose:
                print(f"\n--- {model_config['name']} ---")

            conversations[model_key].append({"role": "user", "content": prompt})
            response = ask_model_with_retry(model_key, conversations[model_key])
            conversations[model_key].append({"role": "assistant", "content": response})

            results["rounds"][str(round_num)][model_key] = response

            if verbose:
                preview = response[:600].replace('\n', ' ')
                print(f"{preview}...")

            time.sleep(3)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"product_consensus_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    summary_file = RUNS_DIR / f"product_consensus_{timestamp}.md"
    with open(summary_file, "w") as f:
        f.write("# Product Design Probe - Consensus Building\n\n")
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

    print(f"Running consensus probe with {rounds} rounds...")
    print("(Includes retry logic for rate limits)")
    run_consensus_probe(max_rounds=rounds)
