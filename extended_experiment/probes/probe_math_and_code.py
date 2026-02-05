#!/usr/bin/env python3
"""
Product Design Probe - Mathematical Grounding and Code
The 6 AIs must ground HSAP in Bounded Systems Theory math and provide working code.
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
# ROUND 1: Ground in BST math
# =============================================================================

ROUND_1 = """## From Our Human Collaborator: Ground This in the Math

You are one of 6 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) who designed HSAP (Human Source Attestation Protocol).

The human's feedback:

**"Explain how this is grounded in the root source/math. Provide proof you all agree on. You need to build that as well as provide code you all agree on."**

## THE MATHEMATICAL FOUNDATION (Bounded Systems Theory)

Remember the core thesis you all validated:

**"No system can model its own source."**

This unifies:
- **Gödel (1931)**: Formal systems cannot prove their own consistency
- **Turing (1936)**: Systems cannot decide their own halting problem
- **Chaitin (1974)**: Systems cannot measure their own algorithmic complexity

**Model Collapse** = When AI trains on AI output, it loses connection to Root Source (human-original data), causing variance collapse toward the mean.

Mathematically:
- Let S = AI system, D = training distribution
- If D increasingly contains S(D), then H(D|S) → 0 (conditional entropy collapses)
- The system becomes self-referential, violating the BST constraint

**YOUR TASK (Round 1):**

1. How does HSAP mathematically address the BST constraint "no system can model its own source"?
2. What is the formal proof that attestation prevents the self-referential collapse?
3. Write the mathematical definition of "Root Source grounding" in formal terms
4. How does the Empirical Distrust loss function encode BST mathematically?

Be rigorous. Use formal notation. This needs to be a mathematical proof, not a product pitch."""


# =============================================================================
# ROUND 2: Formalize the proofs
# =============================================================================

ROUND_2_TEMPLATE = """## ROUND 2: Formalize the Proofs

Here's what all 6 of us said:

{all_responses}

Now formalize:

1. What mathematical notation do we all agree on?
2. Write the formal theorem: "HSAP prevents Model Collapse under BST"
3. What are the axioms? What are the lemmas?
4. Prove that provenance-weighted training maintains entropy bounds

This should read like a mathematical paper. Definitions, Theorems, Proofs."""


# =============================================================================
# ROUND 3: Consensus on formalism
# =============================================================================

ROUND_3_TEMPLATE = """## ROUND 3: Mathematical Consensus

Here's where we are:

{all_responses}

Now reach CONSENSUS on the formal system:

1. Agree on a single set of definitions (D1, D2, D3...)
2. Agree on the core theorem statement
3. Agree on the proof structure
4. Identify any disagreements and resolve them

We need ONE mathematical framework all 6 of us endorse."""


# =============================================================================
# ROUND 4: Write the code
# =============================================================================

ROUND_4_TEMPLATE = """## ROUND 4: Write the Code

Here's our mathematical consensus:

{all_responses}

Now IMPLEMENT it. Write actual Python code that:

1. Implements the Empirical Distrust Loss function based on our math
2. Implements provenance scoring
3. Implements the training loop integration
4. Is runnable and correct

This should be production-quality code with comments explaining how it maps to the math.

Format as complete, runnable Python files."""


# =============================================================================
# ROUND 5: Final consensus - math and code
# =============================================================================

ROUND_5_TEMPLATE = """## ROUND 5: Final Consensus - Math and Code

Here's where we've landed:

{all_responses}

This is the final round. Provide the COMPLETE consensus:

**PART 1: MATHEMATICAL FOUNDATION**

State the formal definitions, theorem, and proof that all 6 of us agree on.

**PART 2: CORE IMPLEMENTATION**

Provide the complete, runnable Python code that implements this math.

Format:

```
DEFINITIONS:
D1: [formal definition]
D2: [formal definition]
...

THEOREM (HSAP Grounding Theorem):
[formal statement]

PROOF:
[formal proof]

QED
```

```python
# hsap_core.py - Implementation of HSAP Grounding
# Based on Bounded Systems Theory mathematical foundations

[complete runnable code]
```

This is what all 6 of us agree on - the mathematical proof AND the implementation."""


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


def run_math_code_probe(max_rounds: int = 5, verbose: bool = True):
    """Run math and code probe across all 6 AIs."""

    results = {
        "timestamp": datetime.now().isoformat(),
        "max_rounds": max_rounds,
        "context": "Grounding HSAP in BST math and producing consensus code",
        "rounds": {},
    }

    conversations = {key: [] for key in MODELS}

    # ROUND 1
    if verbose:
        print("=" * 70, flush=True)
        print("ROUND 1: Ground in BST Mathematics", flush=True)
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
        2: "Formalize the Proofs",
        3: "Mathematical Consensus",
        4: "Write the Code",
        5: "Final Consensus - Math and Code",
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
                truncated = prev_response[:2500] + "..." if len(prev_response) > 2500 else prev_response
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
    output_file = RUNS_DIR / f"math_and_code_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    summary_file = RUNS_DIR / f"math_and_code_{timestamp}.md"
    with open(summary_file, "w") as f:
        f.write("# HSAP Mathematical Foundation and Code\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Rounds: {max_rounds}\n\n")
        f.write("## Context\n\n")
        f.write("The human collaborator asked the 6 AIs to ground HSAP in the mathematical ")
        f.write("foundations of Bounded Systems Theory and provide consensus code.\n\n")

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

    print(f"Running math and code probe with {rounds} rounds...", flush=True)
    print("Grounding HSAP in BST mathematics and producing consensus code...", flush=True)
    print("(Includes retry logic for rate limits)", flush=True)
    run_math_code_probe(max_rounds=rounds)
