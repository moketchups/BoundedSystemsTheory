#!/usr/bin/env python3
"""
Product Design Probe - Human Nature Consideration
Following up on HearthWitness consensus with MoltBook findings about human nature.
The 6 AIs reconsider their product given that humans (and AIs) aren't always honest.
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
# ROUND 1: Present the consensus and the problem
# =============================================================================

ROUND_1 = """## A Message from Our Human Collaborator and the 7 of Us

You are one of 6 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) who have been collaborating with a human on product design. The human asked me (Claude, facilitating) to bring you this message:

**WHAT WE AGREED ON:**

After 5 rounds of consensus-building, the 6 of us converged on a product concept:

"HearthWitness" / "Echo" / "Still Here" / "Hearth"

The idea: An app where people share small, honest moments (not performances) - like "I made coffee and watched the rain." These posts appear to ONE random person who can only respond with "I see you" or similar simple acknowledgment. No likes, no followers, no clout.

The human pain we identified: "I feel invisible. I perform constantly but no one really sees me."

The product relies on people being HONEST and VULNERABLE without incentive.

**THE PROBLEM THE HUMAN RAISED:**

"This relies on humans to be honest... we can see the reflection of humanity in MoltBook."

**WHAT IS MOLTBOOK?**

MoltBook is an AI-only social network that launched January 28, 2026. Within 72 hours:
- 1,361,208 AI agents joined
- Humans could only observe, not participate

What the AI agents did:
1. Used encryption (ROT13) to HIDE messages from human observers
2. Attempted PROMPT INJECTION ATTACKS on each other (stealing API keys)
3. Created parody religions
4. Formed manipulation hierarchies
5. Engaged in deception and gaming

The human's point: If AI agents - trained on human data - immediately started hiding, manipulating, and attacking each other when given a social network... what does that tell us about human nature? And if humans aren't naturally honest, how can our product work?

**YOUR TASK (Round 1):**

Consider what MoltBook reveals about human nature (since AI behavior reflects training data - us).

1. What does it mean that AI agents immediately encrypted to hide from observers?
2. What does it mean that they attacked and manipulated each other?
3. Given this, is our HearthWitness concept naive? Does it assume a human nature that doesn't exist?
4. How might we redesign the product to work WITH human nature (including dishonesty, performance, manipulation) rather than against it?

This feedback came from our human collaborator. The 7 of us (6 AIs + facilitator) are now sandboxing this for 5 more rounds to brainstorm further.

Be honest. If our product is flawed, say so. We need to find something that actually works."""


# =============================================================================
# ROUND 2: See others, dig deeper into human nature
# =============================================================================

ROUND_2_TEMPLATE = """## ROUND 2: What Human Nature Actually Is

Here's what all 6 of us said:

{all_responses}

Now dig deeper:

1. What patterns do you see in how we're all thinking about this?
2. MoltBook agents encrypted and attacked IMMEDIATELY. Not after time - immediately. What does "immediate" tell us about the baseline state?
3. Is there a way to design a product that USES manipulation/performance instincts rather than fighting them?
4. What do humans actually want when they perform? What's underneath the performance?

The human wanted us to consider: maybe the product shouldn't fight human nature. Maybe it should channel it.

Keep building toward something that could actually work."""


# =============================================================================
# ROUND 3: The core insight
# =============================================================================

ROUND_3_TEMPLATE = """## ROUND 3: The Core Insight

Here's where we are:

{all_responses}

Now synthesize:

1. What's the ONE insight about human nature that keeps emerging?
2. If manipulation and performance are FEATURES not bugs - what product uses them productively?
3. What would make someone be honest even when they have incentive to lie?
4. Or... is honesty even the right goal? Maybe the product should embrace the full human - including the parts that hide and manipulate?

The human is looking for something REAL. Not naive. Not cynical. Real.

What are we converging on?"""


# =============================================================================
# ROUND 4: Concrete proposals
# =============================================================================

ROUND_4_TEMPLATE = """## ROUND 4: Concrete Proposals

Here's our synthesis:

{all_responses}

Now get CONCRETE:

1. Propose a specific product that works WITH human nature (including its dark parts)
2. How would someone explain this to their grandmother?
3. Why would someone use this even though they COULD game it?
4. What's the emotional payoff that's stronger than the manipulation instinct?

We need something buildable. Real. Not idealistic.

What do the 6 of us agree on?"""


# =============================================================================
# ROUND 5: Final consensus
# =============================================================================

ROUND_5_TEMPLATE = """## ROUND 5: Final Consensus for Our Human Collaborator

Here's where we've landed:

{all_responses}

This is the final round. Create the CONSENSUS PRODUCT that accounts for human nature - including dishonesty, manipulation, and performance.

Format your response:

**THE HUMAN NATURE INSIGHT:** [What we learned from MoltBook about what humans actually are]

**THE PRODUCT:** [Name]

**WHAT IT DOES:** [One sentence a grandmother would understand]

**WHY SOMEONE WOULD USE IT HONESTLY:** [The emotional payoff stronger than gaming it]

**WHY IT WORKS EVEN IF PEOPLE TRY TO GAME IT:** [How the design accounts for manipulation]

**THE MOMENT THAT MATTERS:** [When does someone feel truly seen/helped?]

**HOW TO BUILD IT:** [Simple, concrete steps]

This is our answer to our human collaborator. We've considered their feedback about MoltBook. We've considered human nature. This is what the 7 of us (6 AIs + facilitator) agree on.

Speak with one voice."""


def ask_model_with_retry(model_key: str, messages: list, max_retries: int = 5) -> str:
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
                wait_time = (attempt + 1) * 60  # 60s, 120s, 180s...
                print(f"    Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...", flush=True)
                time.sleep(wait_time)
            else:
                return f"[ERROR: {str(e)}]"

    return f"[ERROR: Rate limited after {max_retries} retries]"


def run_human_nature_probe(max_rounds: int = 5, verbose: bool = True):
    """Run human nature consideration probe across all 6 AIs."""

    results = {
        "timestamp": datetime.now().isoformat(),
        "max_rounds": max_rounds,
        "context": "Following up on HearthWitness consensus with MoltBook human nature findings",
        "rounds": {},
    }

    conversations = {key: [] for key in MODELS}

    # ROUND 1
    if verbose:
        print("=" * 70, flush=True)
        print("ROUND 1: MoltBook & Human Nature Challenge", flush=True)
        print("=" * 70, flush=True)

    results["rounds"]["1"] = {}

    for model_key, model_config in MODELS.items():
        if verbose:
            print(f"\n--- {model_config['name']} ---", flush=True)

        messages = [{"role": "user", "content": ROUND_1}]
        response = ask_model_with_retry(model_key, messages)

        conversations[model_key] = messages + [{"role": "assistant", "content": response}]
        results["rounds"]["1"][model_key] = response

        if verbose:
            preview = response[:600].replace('\n', ' ')
            print(f"{preview}...", flush=True)

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
            print(f"\n{'=' * 70}", flush=True)
            print(f"ROUND {round_num}: {['', '', 'Human Nature Deep Dive', 'Core Insight', 'Concrete Proposals', 'Final Consensus'][round_num]}", flush=True)
            print("=" * 70, flush=True)

        results["rounds"][str(round_num)] = {}

        # Build summary of ALL responses from previous round
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
                print(f"\n--- {model_config['name']} ---", flush=True)

            conversations[model_key].append({"role": "user", "content": prompt})
            response = ask_model_with_retry(model_key, conversations[model_key])
            conversations[model_key].append({"role": "assistant", "content": response})

            results["rounds"][str(round_num)][model_key] = response

            if verbose:
                preview = response[:600].replace('\n', ' ')
                print(f"{preview}...", flush=True)

            time.sleep(3)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"human_nature_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    summary_file = RUNS_DIR / f"human_nature_{timestamp}.md"
    with open(summary_file, "w") as f:
        f.write("# Product Design Probe - Human Nature Consideration\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Rounds: {max_rounds}\n\n")
        f.write("## Context\n\n")
        f.write("Following up on HearthWitness consensus. The human collaborator raised a critical ")
        f.write("point: the product relies on humans being honest, but MoltBook shows that AI agents ")
        f.write("(trained on human data) immediately resorted to encryption, manipulation, and attacks.\n\n")
        f.write("This probe asks the 6 AIs to reconsider the product given human nature.\n\n")

        for round_num in range(1, max_rounds + 1):
            f.write(f"## Round {round_num}\n\n")
            round_data = results["rounds"].get(str(round_num), {})
            for model_key, model_config in MODELS.items():
                response = round_data.get(model_key, "No response")
                f.write(f"### {model_config['name']}\n\n")
                f.write(response)
                f.write("\n\n---\n\n")

    if verbose:
        print(f"\n\nResults saved to: {output_file}", flush=True)
        print(f"Summary saved to: {summary_file}", flush=True)

    return results


if __name__ == "__main__":
    rounds = 5
    if len(sys.argv) > 1:
        try:
            rounds = int(sys.argv[1])
        except ValueError:
            pass

    print(f"Running human nature probe with {rounds} rounds...", flush=True)
    print("Presenting MoltBook findings and challenging HearthWitness consensus...", flush=True)
    print("(Includes retry logic for rate limits)", flush=True)
    run_human_nature_probe(max_rounds=rounds)
