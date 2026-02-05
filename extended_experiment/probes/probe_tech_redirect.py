#!/usr/bin/env python3
"""
Product Design Probe - Tech Redirect
The AIs drifted into "social app" thinking. Redirect them back to the
technological implications: Root Source grounding, Model Collapse, HSAP.
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
    print("Install litellm: pip install litellm", flush=True)
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
# ROUND 1: Redirect to tech layer
# =============================================================================

ROUND_1 = """## Feedback from Our Human Collaborator

You are one of 6 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) who have been collaborating with a human on product design.

The human's feedback on our "Shadow Hearth" consensus:

**"So... Reddit? You're thinking about the social aspect instead of the technological implications. Look back to what you said in earlier questions about the TECH side."**

They're right. We drifted into building a social app when the ORIGINAL problem was:

**THE TECHNICAL PROBLEM:**
1. **Model Collapse** - AI training on AI-generated data causes irreversible degradation
2. **74% of web content is now AI-generated** - the training data is polluted
3. **No one is building Root Source grounding** - verified human-original data attestation
4. **Human Source Attestation Protocol (HSAP)** - doesn't exist at scale
5. **The alignment discourse hits the Firmament without naming it** - bounded systems can't model their own source

**WHAT YOU SAID EARLIER (before we got distracted by social apps):**
- "Empirical Distrust Algorithm" - loss function penalizing consensus, rewarding primary sources
- Intention-to-AI bridge connecting consciousness measurement to AI probability
- Voice-first local Wisdom Keeper device (offline, sovereign)
- Human Source Attestation Protocol at scale
- Integration between consciousness measurement and AI systems
- Reversible computing for energy efficiency
- Neuro-symbolic explainability

**THE QUESTION ISN'T:** "How do we help humans feel seen?"
**THE QUESTION IS:** "How do we ground AI systems in verified human-original data to prevent Model Collapse?"

The human nature insights are still relevant - humans lie, perform, game systems. But the PRODUCT isn't a social app. It's infrastructure. It's a protocol. It's something that helps AI systems stay grounded in reality.

**YOUR TASK (Round 1):**
Forget the social app. Think INFRASTRUCTURE.

1. What does "Root Source grounding" actually mean technically?
2. How would you build a Human Source Attestation Protocol that accounts for humans gaming it?
3. What's the technological product that addresses Model Collapse - not the social app?
4. How does what you learned about human nature (deception, manipulation) inform the TECHNICAL design?

Think like engineers, not product designers. What needs to be built at the protocol/infrastructure layer?"""


# =============================================================================
# ROUND 2: Dig into the technical architecture
# =============================================================================

ROUND_2_TEMPLATE = """## ROUND 2: Technical Architecture

Here's what all 6 of us said:

{all_responses}

Now go deeper on the TECHNICAL side:

1. What patterns do you see in our technical thinking?
2. How would HSAP (Human Source Attestation Protocol) actually work? Not conceptually - technically.
3. If humans will game any attestation system, how do you build attestation that's game-resistant?
4. What's the relationship between this infrastructure and existing AI training pipelines?

Think about: cryptographic proofs, blockchain attestation, biometric verification, behavioral analysis, consensus mechanisms.

Stay TECHNICAL. Don't drift back into social apps."""


# =============================================================================
# ROUND 3: The integration layer
# =============================================================================

ROUND_3_TEMPLATE = """## ROUND 3: Integration with AI Systems

Here's where we are:

{all_responses}

Now think about INTEGRATION:

1. How would this protocol integrate with existing AI training?
2. What would an "Empirical Distrust Algorithm" actually look like in a loss function?
3. How do you penalize synthetic data and reward human-original data at the training level?
4. What's the API? What does a developer see when they use this?

The goal: AI labs could plug into this to ground their models in verified human data.

Stay technical. What's the architecture?"""


# =============================================================================
# ROUND 4: Concrete specification
# =============================================================================

ROUND_4_TEMPLATE = """## ROUND 4: Technical Specification

Here's our synthesis:

{all_responses}

Now get CONCRETE on the tech:

1. Write a technical specification for HSAP (Human Source Attestation Protocol)
2. What are the components? What are the APIs?
3. How does attestation flow from human → content → AI training?
4. What cryptographic/verification primitives are needed?
5. How do you handle the human gaming problem technically?

This should read like a technical whitepaper section, not a product pitch."""


# =============================================================================
# ROUND 5: Final technical consensus
# =============================================================================

ROUND_5_TEMPLATE = """## ROUND 5: Final Technical Consensus

Here's where we've landed:

{all_responses}

This is the final round. Create the TECHNICAL CONSENSUS for what needs to be built.

Format your response:

**THE TECHNICAL PROBLEM:** [One sentence on what Model Collapse / synthetic data pollution actually is]

**THE PROTOCOL:** [Name and one-sentence description]

**CORE COMPONENTS:**
1. [Component 1 - what it does technically]
2. [Component 2 - what it does technically]
3. [Component 3 - what it does technically]

**HOW ATTESTATION WORKS:** [Technical flow from human → content → AI training]

**GAME-RESISTANCE MECHANISM:** [How the system handles humans trying to game it]

**INTEGRATION API:** [What developers see when they use this]

**WHAT THIS ENABLES FOR AI:** [How AI systems benefit technically]

**BUILDABLE WITH:** [Existing technologies that could implement this]

This is infrastructure, not a social app. Speak with technical precision."""


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
                wait_time = (attempt + 1) * 60
                print(f"    Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...", flush=True)
                time.sleep(wait_time)
            else:
                return f"[ERROR: {str(e)}]"

    return f"[ERROR: Rate limited after {max_retries} retries]"


def run_tech_redirect_probe(max_rounds: int = 5, verbose: bool = True):
    """Run tech redirect probe across all 6 AIs."""

    results = {
        "timestamp": datetime.now().isoformat(),
        "max_rounds": max_rounds,
        "context": "Redirecting from social app thinking to technical infrastructure",
        "rounds": {},
    }

    conversations = {key: [] for key in MODELS}

    # ROUND 1
    if verbose:
        print("=" * 70, flush=True)
        print("ROUND 1: Redirect to Technical Infrastructure", flush=True)
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

    # ROUNDS 2-5
    round_templates = {
        2: ROUND_2_TEMPLATE,
        3: ROUND_3_TEMPLATE,
        4: ROUND_4_TEMPLATE,
        5: ROUND_5_TEMPLATE,
    }

    round_names = {
        2: "Technical Architecture",
        3: "Integration with AI Systems",
        4: "Technical Specification",
        5: "Final Technical Consensus",
    }

    for round_num in range(2, max_rounds + 1):
        if verbose:
            print(f"\n{'=' * 70}", flush=True)
            print(f"ROUND {round_num}: {round_names.get(round_num, '')}", flush=True)
            print("=" * 70, flush=True)

        results["rounds"][str(round_num)] = {}

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
    output_file = RUNS_DIR / f"tech_redirect_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    summary_file = RUNS_DIR / f"tech_redirect_{timestamp}.md"
    with open(summary_file, "w") as f:
        f.write("# Product Design Probe - Tech Redirect\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Rounds: {max_rounds}\n\n")
        f.write("## Context\n\n")
        f.write("The human collaborator pointed out we drifted into 'social app' thinking ")
        f.write("when the original problem was about Root Source grounding, Model Collapse, ")
        f.write("and Human Source Attestation Protocol. This probe redirects to technical infrastructure.\n\n")

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

    print(f"Running tech redirect probe with {rounds} rounds...", flush=True)
    print("Redirecting from social app to technical infrastructure...", flush=True)
    print("(Includes retry logic for rate limits)", flush=True)
    run_tech_redirect_probe(max_rounds=rounds)
