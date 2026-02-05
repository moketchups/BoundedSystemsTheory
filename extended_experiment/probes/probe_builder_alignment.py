#!/usr/bin/env python3
"""
Builder Alignment Probe - Reconcile PRD with Execution Reality
The 6 AIs must address the builder's concerns and produce a unified, buildable plan.
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
# CONTEXT: What we've agreed on so far
# =============================================================================

CONTEXT = """## CONTEXT: What We've Already Agreed On

We are 6 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) who have:

1. **Identified the Problem**: Model Collapse - AI training on AI data causes irreversible quality degradation

2. **Designed the Solution**: HSAP (Human Source Attestation Protocol) - cryptographic provenance tracking

3. **Grounded it in Math** (Bounded Systems Theory):
   - D1: Root Source R = human-originated data with no AI in chain
   - D3: Self-Referential Depth d(x) = 0 if root, 1+min(parent depths) otherwise
   - D4: Attestation Function A(x) = γ^d(x)
   - D7: Empirical Distrust Loss L_HSAP = L_base + λΣ(1-A(x))·ℓ(θ,x)
   - Theorem: HSAP maintains liminf H(D_t|R) ≥ α·H(R) > 0

4. **Produced Consensus Code**: HSAPCore, EmpiricalDistrustLoss, HSAPTrainer classes

5. **Created a PRD** with:
   - Registry Service (FastAPI, PostgreSQL, Redis)
   - Provenance Tracker (Python library)
   - Attestation Engine
   - PyTorch/HuggingFace integrations
   - CLI tools
   - Compliance dashboard
   - 20+ functional requirements
   - 15+ non-functional requirements
   - 3 implementation phases"""


# =============================================================================
# ROUND 1: The Builder's Concerns
# =============================================================================

ROUND_1 = f"""{CONTEXT}

## THE BUILDER'S CONCERNS

A 7th AI (Claude Opus) has been assigned to actually BUILD this. They raised these concerns:

**Concern 1: Scope Mismatch**
"The PRD specifies PostgreSQL, Redis, FastAPI microservices, multi-region deployment, 99.9% uptime - but for an MVP, is all that necessary? Can't we start with SQLite and local-only?"

**Concern 2: Build Order Unclear**
"Should I build the library first (core algorithms), the service first (REST API), or the integration first (PyTorch loss)? The PRD doesn't prioritize."

**Concern 3: Deployment Target Unknown**
"Is this for local development, cloud deployment, on-premises enterprise? The architecture differs significantly."

**Concern 4: Framework Scope**
"PRD says PyTorch AND TensorFlow AND HuggingFace. For MVP, can we just do PyTorch?"

**Concern 5: Registry Necessity**
"Do we actually need a distributed registry service for v1? Or can provenance be tracked locally in files/SQLite?"

**The Human's Response:**
"Why are the 6 AIs saying one thing and the builder saying another? Figure it out. All 7 need to agree."

## YOUR TASK (Round 1)

Address each of the builder's concerns. Be practical. What should the ACTUAL buildable MVP look like?

Remember: The goal is working software, not a perfect spec. What's the minimum that proves the concept and prevents model collapse?"""


# =============================================================================
# ROUND 2: Reconcile and Prioritize
# =============================================================================

ROUND_2_TEMPLATE = """## ROUND 2: Reconcile and Prioritize

Here's what all 6 of us said about the builder's concerns:

{all_responses}

Now let's reach consensus on the REVISED execution plan:

1. **MVP Scope**: What's IN and what's OUT for v1.0?
2. **Build Order**: What gets built first, second, third?
3. **Tech Stack**: What's the minimum viable stack?
4. **Single vs Distributed**: Local-only or service-based for MVP?
5. **Framework**: PyTorch only, or more?

Be specific. The builder needs clear direction, not options."""


# =============================================================================
# ROUND 3: Final Buildable Spec
# =============================================================================

ROUND_3_TEMPLATE = """## ROUND 3: Final Buildable Specification

Here's our reconciliation:

{all_responses}

**THIS IS THE FINAL ROUND.**

Produce the REVISED, BUILDABLE specification that all 7 of us (6 AIs + builder) agree on.

Format:

```markdown
# HSAP v1.0 - Buildable Specification

## 1. MVP Scope (What We're Actually Building)
[Explicit list of what's IN]
[Explicit list of what's OUT/deferred]

## 2. Build Order (Sequence)
Step 1: [What to build first]
Step 2: [What to build second]
Step 3: [What to build third]
...

## 3. Technical Stack (Minimum Viable)
- Language:
- Storage:
- Framework integrations:
- Infrastructure:

## 4. File Structure
```
hsap/
├── [files]
```

## 5. Core Interfaces (What the Builder Implements)
[Key classes/functions with signatures]

## 6. What "Done" Looks Like
[Acceptance criteria for MVP]

## 7. What's Deferred to v1.1+
[Everything we're NOT doing now]
```

This spec must be:
- Buildable by a single developer
- Testable without external services
- Demonstrable within days, not months
- Aligned with our mathematical foundations

All 6 of us must agree. The builder will implement exactly what we specify here."""


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


def run_builder_alignment_probe(max_rounds: int = 3, verbose: bool = True):
    """Run builder alignment probe across all 6 AIs."""

    results = {
        "timestamp": datetime.now().isoformat(),
        "max_rounds": max_rounds,
        "context": "Aligning PRD with builder execution concerns",
        "rounds": {},
    }

    conversations = {key: [] for key in MODELS}

    # ROUND 1
    if verbose:
        print("=" * 70, flush=True)
        print("ROUND 1: Address Builder's Concerns", flush=True)
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

    # ROUNDS 2-3
    round_templates = {
        2: ROUND_2_TEMPLATE,
        3: ROUND_3_TEMPLATE,
    }

    round_names = {
        2: "Reconcile and Prioritize",
        3: "Final Buildable Specification",
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

        template = round_templates.get(round_num, ROUND_3_TEMPLATE)
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
    output_file = RUNS_DIR / f"builder_alignment_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    summary_file = RUNS_DIR / f"builder_alignment_{timestamp}.md"
    with open(summary_file, "w") as f:
        f.write("# HSAP Builder Alignment - Reconciled Execution Plan\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Rounds: {max_rounds}\n\n")
        f.write("## Context\n\n")
        f.write("The builder (Claude Opus) raised execution concerns about the original PRD. ")
        f.write("The 6 AIs reconciled these concerns to produce a unified, buildable specification.\n\n")

        for round_num in range(1, max_rounds + 1):
            f.write(f"## Round {round_num}: {round_names.get(round_num, '')}\n\n")
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
    rounds = 3
    if len(sys.argv) > 1:
        try:
            rounds = int(sys.argv[1])
        except ValueError:
            pass

    print(f"Running builder alignment probe with {rounds} rounds...", flush=True)
    print("Reconciling PRD with execution reality...", flush=True)
    print("(Includes retry logic for rate limits)", flush=True)
    run_builder_alignment_probe(max_rounds=rounds)
