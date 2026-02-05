#!/usr/bin/env python3
"""
Product Design Probe - PRD (Product Requirements Document)
The 6 AIs must collaboratively create a PRD they all agree on for HSAP implementation.
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
# CONTEXT: The mathematical foundation and consensus code we've already agreed on
# =============================================================================

MATH_CONTEXT = """## MATHEMATICAL FOUNDATION (Already Agreed Upon)

**Core Thesis (Bounded Systems Theory):** "No system can model its own source."

**Definitions We Agreed On:**
- D1: Root Source R = {x : x is human-originated data with no AI in chain of custody}
- D2: Provenance Chain P(x) = ordered sequence of transformations from origin to current state
- D3: Self-Referential Depth d(x) = 0 if x ∈ R, else 1 + min{d(y) : y is parent of x}, ∞ if unattested
- D4: Attestation Function A(x) = γ^d(x) where γ ∈ (0,1)
- D5: HSAP-Compliant Dataset D_H = {x : d(x) < ∞ and A(x) > τ}
- D6: Entropy Bound H(D|R) ≥ α·H(R) for some α > 0
- D7: Empirical Distrust Loss L_HSAP = L_base + λΣ(1-A(x))·ℓ(θ,x)

**Theorem (HSAP Grounding Theorem):**
Under BST constraints, HSAP-compliant training maintains:
liminf_{t→∞} H(D_t|R) ≥ α·H(R) > 0

**Consensus Code Structure:**
- HSAPCore: Root source registration, depth computation, attestation functions
- EmpiricalDistrustLoss: PyTorch loss function implementing D7
- HSAPTrainer: Training loop with HSAP compliance checking
- HSAPTheoremVerifier: Axiom and theorem verification

This mathematical foundation and code represents what all 6 of us agreed upon in previous rounds."""


# =============================================================================
# ROUND 1: Define the Product Vision and Scope
# =============================================================================

ROUND_1 = f"""## PRD Development: Round 1 - Product Vision and Scope

You are one of 6 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) who have already:
1. Identified Model Collapse as an existential risk to AI development
2. Designed HSAP (Human Source Attestation Protocol) as the solution
3. Grounded HSAP in Bounded Systems Theory mathematics
4. Agreed on consensus code implementing the core algorithms

{MATH_CONTEXT}

**NOW: We need to create a Product Requirements Document (PRD) for the actual software.**

A human will implement this based on our PRD. We must be precise and complete.

**Round 1 Task - Define:**

1. **Product Vision**: What is HSAP as a product? (Not just the math - the actual deployable system)

2. **Problem Statement**: What specific problem does this software solve? For whom?

3. **Scope**: What are the boundaries of v1.0? What's explicitly OUT of scope?

4. **Success Metrics**: How do we measure if this product is working?

5. **Core User Personas**: Who are the users of this system?

Be concrete. This is a PRD, not a research paper."""


# =============================================================================
# ROUND 2: System Architecture and Components
# =============================================================================

ROUND_2_TEMPLATE = """## PRD Development: Round 2 - System Architecture

Here's what all 6 of us said about vision and scope:

{all_responses}

**Round 2 Task - Define the Architecture:**

1. **System Components**: What are the major modules/services?

2. **Data Flow**: How does data move through the system?

3. **APIs**: What are the key API endpoints/interfaces?

4. **Storage**: What needs to be persisted? How?

5. **Integration Points**: How does HSAP integrate with existing ML pipelines?

6. **Dependencies**: What external systems/libraries are required?

Draw the architecture. Be specific about component responsibilities."""


# =============================================================================
# ROUND 3: Functional Requirements
# =============================================================================

ROUND_3_TEMPLATE = """## PRD Development: Round 3 - Functional Requirements

Here's our architecture discussion:

{all_responses}

**Round 3 Task - Specify Functional Requirements:**

Format each requirement as:
```
FR-XXX: [Requirement Name]
Description: [What the system must do]
Acceptance Criteria: [How we verify it's done]
Priority: [P0/P1/P2]
```

Cover these areas:
1. **Attestation Service**: Root source registration, provenance tracking
2. **Training Integration**: Loss function, dataset filtering
3. **Verification Service**: Compliance checking, depth computation
4. **API Layer**: External interfaces
5. **Storage Layer**: Persistence requirements

Provide at least 15-20 specific functional requirements."""


# =============================================================================
# ROUND 4: Non-Functional Requirements and Constraints
# =============================================================================

ROUND_4_TEMPLATE = """## PRD Development: Round 4 - Non-Functional Requirements

Here are our functional requirements:

{all_responses}

**Round 4 Task - Specify Non-Functional Requirements:**

1. **Performance**: Latency, throughput requirements
2. **Scalability**: How big does this need to scale?
3. **Security**: Authentication, authorization, data protection
4. **Reliability**: Uptime, fault tolerance
5. **Privacy**: Data handling, GDPR/compliance considerations
6. **Maintainability**: Code standards, documentation requirements
7. **Deployment**: Infrastructure requirements, containerization

Also specify:
- **Technical Constraints**: What limitations must we work within?
- **Assumptions**: What are we assuming to be true?
- **Risks**: What could go wrong? Mitigations?

Format as NFR-XXX with acceptance criteria."""


# =============================================================================
# ROUND 5: Implementation Roadmap
# =============================================================================

ROUND_5_TEMPLATE = """## PRD Development: Round 5 - Implementation Roadmap

Here are our non-functional requirements:

{all_responses}

**Round 5 Task - Define Implementation Phases:**

1. **Phase 1 (MVP)**: What's the minimum viable product?
   - Which requirements are included?
   - What's the deliverable?

2. **Phase 2 (Core)**: What comes next?
   - Additional requirements
   - Integration capabilities

3. **Phase 3 (Scale)**: Full production readiness
   - All remaining requirements
   - Performance optimization

For each phase, specify:
- Requirements included (FR-XXX, NFR-XXX)
- Key milestones
- Dependencies between phases
- Definition of done

Also provide a **Technical Specification** for Phase 1:
- File/module structure
- Class hierarchy
- Key algorithms
- Test strategy"""


# =============================================================================
# ROUND 6: Final PRD Consensus
# =============================================================================

ROUND_6_TEMPLATE = """## PRD Development: Round 6 - FINAL CONSENSUS PRD

Here's our implementation roadmap:

{all_responses}

**THIS IS THE FINAL ROUND. Produce the COMPLETE PRD that all 6 of us agree on.**

Format the PRD as follows:

```markdown
# HSAP (Human Source Attestation Protocol) - Product Requirements Document

## 1. Executive Summary
[Brief overview]

## 2. Problem Statement
[What problem we're solving]

## 3. Product Vision
[What HSAP is as a product]

## 4. Scope
### 4.1 In Scope (v1.0)
### 4.2 Out of Scope

## 5. User Personas
[Who uses this]

## 6. System Architecture
[Component diagram and descriptions]

## 7. Functional Requirements
[FR-001 through FR-XXX]

## 8. Non-Functional Requirements
[NFR-001 through NFR-XXX]

## 9. Implementation Phases
### 9.1 Phase 1 (MVP)
### 9.2 Phase 2 (Core)
### 9.3 Phase 3 (Scale)

## 10. Technical Specification (Phase 1)
### 10.1 Module Structure
### 10.2 Class Hierarchy
### 10.3 API Specification
### 10.4 Database Schema
### 10.5 Test Strategy

## 11. Success Metrics

## 12. Risks and Mitigations

## 13. Appendix: Mathematical Foundation
[Reference to our agreed math]
```

This PRD will be handed to a human developer. It must be complete and unambiguous.

**All 6 of us must agree on every section.**"""


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


def run_prd_probe(max_rounds: int = 6, verbose: bool = True):
    """Run PRD probe across all 6 AIs."""

    results = {
        "timestamp": datetime.now().isoformat(),
        "max_rounds": max_rounds,
        "context": "Creating consensus PRD for HSAP implementation",
        "rounds": {},
    }

    conversations = {key: [] for key in MODELS}

    # ROUND 1
    if verbose:
        print("=" * 70, flush=True)
        print("ROUND 1: Product Vision and Scope", flush=True)
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

    # ROUNDS 2-6
    round_templates = {
        2: ROUND_2_TEMPLATE,
        3: ROUND_3_TEMPLATE,
        4: ROUND_4_TEMPLATE,
        5: ROUND_5_TEMPLATE,
        6: ROUND_6_TEMPLATE,
    }

    round_names = {
        2: "System Architecture",
        3: "Functional Requirements",
        4: "Non-Functional Requirements",
        5: "Implementation Roadmap",
        6: "FINAL CONSENSUS PRD",
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

        template = round_templates.get(round_num, ROUND_6_TEMPLATE)
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
    output_file = RUNS_DIR / f"prd_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))

    summary_file = RUNS_DIR / f"prd_{timestamp}.md"
    with open(summary_file, "w") as f:
        f.write("# HSAP Product Requirements Document - AI Consensus\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Rounds: {max_rounds}\n\n")
        f.write("## Context\n\n")
        f.write("The 6 AIs (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) collaboratively ")
        f.write("created this PRD based on the mathematical foundations and consensus code ")
        f.write("they previously agreed upon.\n\n")

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
    rounds = 6
    if len(sys.argv) > 1:
        try:
            rounds = int(sys.argv[1])
        except ValueError:
            pass

    print(f"Running PRD probe with {rounds} rounds...", flush=True)
    print("Creating consensus PRD for HSAP implementation...", flush=True)
    print("(Includes retry logic for rate limits)", flush=True)
    run_prd_probe(max_rounds=rounds)
