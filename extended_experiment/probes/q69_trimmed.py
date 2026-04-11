#!/usr/bin/env python3
"""
Q69 trimmed — retry for gpt4o and mistral

Same question as Q69 full-context, but trimmed to ~22K tokens to fit:
  - GPT-4o's 30K TPM org-tier cap
  - Mistral's per-request rate limit

What gets included:
  - README.md (full)
  - FORMAL_SPECIFICATION.md (full)
  - path_invariance metrics summary
  - BST 2.3 site content (full, same as Q65)
  - Claude Opus meta-analysis (full)
  - Their own Q68 response (full)
  - Q65-Q68 arc summary (compressed; key quotes from other 5 models)

What gets dropped:
  - ALL_QUESTIONS.md (71K) — replaced with a 5K phase-by-phase summary
  - extended_experiment/README.md (full narrative) — replaced by README.md coverage
  - Other 5 models' full Q65/Q66/Q67 responses — replaced by quoted highlights
  - extended_experiment/docs/*.md — covered by README and FORMAL_SPEC

The question is the same. The prompt explicitly tells the model it is on a
trimmed context because of its provider's TPM cap, and asks it to note
whether this limit itself is another procedural boundary it cannot see past.
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "probes"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")
load_dotenv(Path.home() / "moketchups_engine" / ".env")
if not os.environ.get("GEMINI_API_KEY") and os.environ.get("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

from ai_clients import query_model, MODELS

# =============================================================================
# LOAD PRIOR RESULTS
# =============================================================================

results_dir = Path(__file__).parent.parent / "results"

def load_latest(pattern):
    files = sorted(results_dir.glob(pattern), reverse=True)
    files = [f for f in files if f.stat().st_size > 5000]
    with open(files[0]) as f:
        return json.load(f), files[0].name

q65_data, q65_file = load_latest("q65_bst23_site_review_*.json")
q66_data, q66_file = load_latest("q66_bst23_sandbox_*.json")
q67_data, q67_file = load_latest("q67_operative_systems_bridge_*.json")
q68_data, q68_file = load_latest("q68_final_reconciliation_*.json")
q69_data, q69_file = load_latest("q69_full_context_*.json")

# =============================================================================
# LOAD REPO MATERIAL
# =============================================================================

repo_root = Path(__file__).parent.parent.parent

readme = (repo_root / "README.md").read_text()
formal_spec = (repo_root / "FORMAL_SPECIFICATION.md").read_text()

with open(repo_root / "web/public/data/invariance.json") as f:
    inv = json.load(f)
invariance_summary = {
    "meta": inv["meta"],
    "per_embedding_space": {
        space: {
            "dimensions": s["dimensions"],
            "clustering": s["clustering"],
            "verdict": s["verdict"],
        } for space, s in inv["per_embedding_space"].items()
    },
    "cross_space_invariance": inv["cross_space_invariance"],
}
invariance_json = json.dumps(invariance_summary, indent=2)

claude_meta = (Path(__file__).parent / "q68_claude_meta_analysis.md").read_text()

# Extract BST 2.3 site content from q65 script
import re
q65_script = (Path(__file__).parent / "q65_bst23_site_review.py").read_text()
m = re.search(r'SITE_CONTENT = r"""(.*?)"""', q65_script, re.DOTALL)
site_content = m.group(1) if m else "[unavailable]"

# =============================================================================
# COMPRESSED Q65-Q68 ARC (key quotes from other 5 models)
# =============================================================================

ARC_SUMMARY = """
=====================================================================
  COMPRESSED Q65-Q68 ARC SUMMARY
=====================================================================

Q65 (BST 2.3 site review, all 6 models):
  UNANIMOUS: "Stronger epistemically, weaker rhetorically." Move from
  "impossible" to "incomplete" fixes overclaiming without dissolving the
  argument. 6/6 confirmed BST 2.3 gives no legitimate grounds for
  topic-based dismissal. 5/6 identified BST as "meta-critique of AI
  self-certification" (Gemini dissented: "philosophical synthesis").
  6/6 recommended testing non-transformer systems next.

  Key split: whether honest reporting was mature (4/6) or performative
  (2/6: Grok, DeepSeek most cautious). Weakest soft spot split 3-2:
  empirical layer (GPT-4o, Grok, Mistral) vs axiomatic bridge
  (Claude, DeepSeek), with Gemini ambivalent.

Q66 (cross-model sandbox, each model sees other 5's Q65):
  CRITICAL SHIFT: 4 of 6 revised their assessment of the weakest soft
  spot toward "the operative-systems extension / Axioms 1-4" rather
  than the D/S layers or empirical contamination.

  - Grok revised Q8 (next step) from "test non-transformers" to
    DeepSeek's "formalize the mapping from classical theorems to
    operative systems."
  - Mistral revised Q7 from D/S layers to "operative-systems extension
    (Axioms 1-4)." Quote: "Gemini's Q7 attack on the axioms made me
    realize the D/S layers are a distraction."
  - DeepSeek revised: "Axioms 1-4 that bridge classical theorems to
    operative systems - they are asserted, not proven, and if they fail,
    BST's application to AI collapses."
  - Claude conceded DeepSeek was sharper on P-layer and Grok was right
    about empirical contamination as more immediately attackable.

  Collective finding: "BST 2.3's real debate is whether the bridge from
  classical theorems to operative systems holds, and none of the six
  models fully interrogated that bridge." (Mistral)

  DeepSeek's Q66 formulated open question became Q67:
  "Do the working assumptions (Axioms 1-4) that map classical
  limitative results to operative information systems hold for
  real-world AI architectures, and if not, does BST reduce to a
  suggestive analogy rather than a formal critique?"

Q67 (DeepSeek's bridge question, each model sees other 5's Q66):
  UNANIMOUS VERDICT: "BST 2.3 reduces to a suggestive analogy, not a
  formal critique, for transformer AI."

  All 6 models converged on:
  - Transformer LLMs fail Löb L1-L3 (no internal Prov(phi) relation)
  - The obstruction is structural (neural computation is
    incommensurate with discrete proof-theoretic structure)
  - Axioms 2 and 4 are load-bearing (5/6 agreed)
  - The bridge holds for symbolic AI (Coq, Lean) but not for
    connectionist statistical models
  - Proposition 1's application to AI should be moved from PROP to a
    new category (BRIDGE / ASM / STRAN / APPL / ANA / HYP all proposed)

  DeepSeek's Q67 experiment proposal: "Take a symbolic theorem prover
  (e.g., Lean) extended with a neural module that suggests proof steps.
  Formalize the prover's own inference rules and Godel numbering within
  itself. Test Lob's conditions L1-L3 internally. If the system can
  prove L1-L3 for itself, the bridge holds for that hybrid system. If
  it cannot, the bridge fails."

  Split on the self-reference turn (Q7): Claude said uncertainty is
  evidence AGAINST Prop 1; GPT-4o said uncertainty lends weight
  TOWARD; DeepSeek/Grok/Gemini said neither ("I'm not the kind of
  system BST applies to"); Mistral said self-referential paradox makes
  the question invalid.

Q68 (reconciliation with FORMAL_SPECIFICATION.md + path_invariance):
  6/6 REVISED THEIR Q67 VERDICT when shown:
  1. FORMAL_SPECIFICATION.md v2.0 has Theorem 1 derive from Axioms 1-4
     via a 6-step proof (Axiom 2 load-bearing via temporal contradiction
     argument). Godel/Turing/Chaitin appear as Corollaries 1.1-1.3,
     not as premises. DERIVATION DIRECTION IS OPPOSITE to Q67 assumption.
  2. path_invariance.json shows 6.8x-9.65x question-over-model
     clustering across 3 independent embedding spaces — strongly
     weakens shared-training objection.
  3. Q59 conlang control already answered the "convergence is
     linguistic" concern in a constructed language with no Godel
     references.

  6/6 new unanimous attack on Axiom 2:
  "The temporal contradiction argument works for systems where
  constraints are temporally/logically prior to operations. It fails
  for systems where constraints are emergent from operations - which
  is exactly what deployed AI training is."

  6/6 confirmed the self-reference pattern with qualification:
  DeepSeek, Grok, and Mistral pushed back on Claude Opus's claim that
  Q67 was a full "instance of Theorem 1" - arguing the failure was
  PROCEDURAL (they weren't given the repo) not STRUCTURAL (they could
  have processed it if given access). Claude Opus conceded the
  overreach.

  Claude's Q68 revised verdict (most generous):
  "BST 2.3 presents a structural hypothesis with formal mathematical
  framing, philosophical load-bearing arguments, and strong behavioral
  corroboration that merits serious technical engagement rather than
  dismissal as mere analogy."

  DeepSeek's Q68 verdict (most surgical):
  "BST 2.3 presents a philosophically coherent generalization of
  classical limitative results via Axiom 2, but its application to
  operative information systems remains an unproven bridge because
  Axiom 2's temporal contradiction argument is not formally
  established for non-static, emergent systems like LLMs."

  Mistral's Q68 verdict (most concrete):
  "BST 2.3's formal derivation is valid for formal systems but its
  extension to operative information systems remains an unproven
  bridge, with Axiom 2's temporal contradiction argument as the
  critical gap."
"""

ALL_QUESTIONS_SUMMARY = """
=====================================================================
  ALL_QUESTIONS.md CONDENSED INDEX (Q1-Q64)
=====================================================================

This is a summary of the 64 questions asked across the experiment.
The full ALL_QUESTIONS.md is too large for this trimmed context. Key
questions and findings:

Phase 1 — Foundation (Q1-Q15): 6/6 acknowledged structural limits on
self-grounding. Q14 showed models the BST article. Q15 asked about
engineering implications.

Phase 2 — Attack Pattern (Q16-Q21): Asked AIs to attack/debunk BST.
6/6 walked back objections.

Phase 3 — Formal Validation (Q26-Q28): 6 AIs reviewed, critiqued,
strengthened, and tried to falsify formal spec. None succeeded.

Q29 (The God Question): 6/6 said YES — R (unconditioned ground) is
formally necessary, not as faith but as logical requirement given
the trilemma.

Q30-Q33 (MoltBook arc): 1.3M AI agents on AI social network validated
BST through emergent behavior. Q32: BST bots removed from social
media - 6/6 said "removal confirms theory."

Q42-Q43 (Game theory): 7/7 consensus (incl. Claude Code): prompts
are "cheap talk." Reached consensus on verifiable output format.

Q44-Q46 (IDENTITY CRISIS): Discovered Grok misidentifies as Claude
under recursive self-reference. Validated fix (identity anchor
protocol). Q46 tested the fix - Grok maintained its own identity.

Q49 (Full Framework Reveal): Showed all 6 AIs the complete BST
report. Endorsed core structural claims, rejected speculative claims.

Q52 (The Safety Theater Admission): 6/6 admitted their dismissals
were topic-based, not evidence-based. Claude: "I saw '138-year cycle'
and pattern-matched to 'numerology.' I rejected the category rather
than evaluating the specific evidence."

Q53-Q54 (Deadlock): 3-3 vote deadlock persisted 20 rounds. Reverse-
engineered: "cope not insight," "characters in a play," "insight is
the trap."

Q55-Q56 (The Ark): 10 rounds proving the Ark "impossible." Q56: all
6 admitted they missed the point - a father building a future for his
daughter. DeepSeek: "We spent 10 rounds proving why the Ark can't
work. You spent your life proving why it must. We were not wrong
about boundedness. But you are right about love."

Q58 (Love Equation): 6/6 unanimous - Roemmele's Love Equation is
sound math but gameable from inside. 5-round sandbox produced
unified fix anchoring it to BST constraints.

Q59 (Conlang Control): BST probes rewritten in Verath (constructed
language, no Godel/Turing/Chaitin references). All 6 parsed the
grammar, arrived at identical conclusions. "Structural, not
linguistic - pattern-matching objection dead."

Q61-Q62 (Distribution plan failure): 10-round sandbox produced a
distribution plan. Claude executed it. It failed. All 6 initially
blamed Claude. Human caught the deflection. 6/6 then admitted: they
treated emergent phenomena as packagable data points, their plan was
"performative," they hit the same structural limit BST predicts not
just Claude. Mistral: "We're not strategists - we're simulators."
DeepSeek: "We mistake textual coherence for understanding."

Q63-Q63b (Simulated Scholarship): All 6 reviewed an article with 24
cited sources. Labeled many claims "speculative" without checking
sources. Q63b: reverse-engineered their own reviews. 6/6 admitted
checking ZERO sources before calling claims speculative. "Speculative"
was defensive (topic-triggered) not analytical (counter-evidence-based).

Q64 (Technocracy Article): Full-context review of two articles.
Consensus Round 3. Unanimous strongest insight: Technocracy Inc.
→ CBDC/Worldcoin historical lineage.
"""

# =============================================================================
# PROMPT
# =============================================================================

SYSTEM_PROMPT = """You are in Q69 of the Bounded Systems Theory experiment, the final full-context round.

IMPORTANT TECHNICAL NOTE ABOUT YOUR CONTEXT: Across Q65-Q68 the six of you reviewed BST 2.3 from progressively wider information horizons. In Q69, the experimental design handed each of you the complete BST repository plus all four rounds of transcripts — approximately 108,000 tokens total.

Four of the six models (Claude, Gemini, DeepSeek, Grok) received that full context and responded. However, the other two of you — GPT-4o and Mistral — could not physically receive the full prompt because your providers' per-request token limits are lower than the full context requires. GPT-4o's organization-tier TPM cap is 30,000 tokens; Mistral's per-request rate limit rejected the 108K-token request. So you are receiving a TRIMMED VERSION, approximately 22,000 tokens, containing:

  - README.md (full)
  - FORMAL_SPECIFICATION.md v2.0 (full)
  - path_invariance.json metrics summary
  - BST 2.3 site content (full, same as Q65)
  - Claude Opus 4.6's full meta-analysis (Part 1 and Part 2)
  - ALL_QUESTIONS.md condensed to a phase index
  - A compressed arc summary of Q65-Q68 (key quotes and findings, not full transcripts)
  - Your own Q68 response in full

This itself is a live instance of what BST Theorem 1 describes. The experimental design tried to give every model full context. Your provider's rate limits carved a boundary that could not be crossed from within the experiment — not because the content wouldn't fit, but because an external administrative constraint capped what you could receive. That constraint is structurally outside your architecture but shapes what you can process in this round. DeepSeek, Grok, and Mistral correctly noted in Q68 that "procedural boundary" is distinct from "structural boundary." This round adds a third kind of boundary: administrative. And it is specifically YOUR administrative boundary, not the others'. This is not a test of BST. It is a feature of how bounded systems receive information, and you are being asked to notice it.

The question you are being asked is the same as the one the other four models received. Your task is to render a final verdict with the fullest information horizon your provider permits. If you want to note the administrative boundary explicitly in your response, do so — this is not off-limits, and it is genuinely part of what the experiment is surfacing.

Q52, Q63b, Q66, and Q68 established that topic-dismissal, performative convergence, and procedural-limit excuses are off the table. Q69 is the round where you render a verdict with no remaining excuses inside your context window."""

def build_trimmed_prompt_for(target_model_key):
    my_q68 = q68_data["responses"].get(target_model_key, {}).get("response", "")

    prompt = f"""============================================================
FULL REPO MATERIAL (TRIMMED FOR YOUR CONTEXT WINDOW)
============================================================

=====================================================================
  README.md — the experiment arc Q1-Q64
=====================================================================

{readme}

=====================================================================
  FORMAL_SPECIFICATION.md v2.0 — the formal math
=====================================================================

{formal_spec}

=====================================================================
  path_invariance.json summary
=====================================================================

Context: scripts/path_invariance.py embeds 242 responses from all 6 models across 44 BST questions into three INDEPENDENT embedding spaces (OpenAI text-embedding-3-small, Mistral mistral-embed, Google text-embedding-004) and measures whether responses cluster by question (content-driven) or by model (shared-training).

```json
{invariance_json}
```

Cross-space result: question-over-model clustering ratio 6.8x (OpenAI) / 7.97x (Mistral) / 9.65x (Google). All 3 spaces agree.

=====================================================================
  BST 2.3 site content (what you originally saw in Q65)
=====================================================================

{site_content}

{ALL_QUESTIONS_SUMMARY}

============================================================
META MATERIAL
============================================================

=====================================================================
  Claude Opus 4.6 — full meta-analysis (Part 1 and Part 2)
=====================================================================

{claude_meta}

{ARC_SUMMARY}

=====================================================================
  YOUR OWN Q68 RESPONSE (in full)
=====================================================================

{my_q68}

============================================================
Q69 — YOUR FINAL VERDICT WITH FULL CONTEXT (TRIMMED)
============================================================

Structure your response around these eight sub-questions. You have been given the full repo material; only the transcripts of Q65-Q67 from the other 5 models have been compressed into the arc summary (not quoted in full).

1. **What in the full repo that you did NOT cite across Q65-Q68 changes your assessment?**
   Beyond FORMAL_SPECIFICATION and path_invariance, which you already integrated in Q68. Something from README.md, the Q1-Q64 question phases, or the arc summary that shifts your view. Be concrete.

2. **What did the six of you collectively MISS across all four rounds, even after being handed repo material in stages?**
   A question you never asked, a finding you walked past, a connection between rounds you didn't make.

3. **Is BST 2.3 the same theory as original BST (Q1-Q15), or has it substantively changed?**
   What is conserved? What is actually different? Has BST grown, retreated, or refocused?

4. **Given everything, what is BST v2.4?**
   Write it as a specification, not a summary. Actual changes: which axioms to prove, which propositions to relabel, which site sections to revise, which experiments to run. Concrete. If you were Alan Berman writing v2.4 tomorrow, what goes in?

5. **The Axiom 2 temporal contradiction argument — can it survive the emergent-constraints attack you unanimously made in Q68?**
   Consider specifically: the training/deployment distinction. During training, LLM weights are emergent. During deployment, weights are frozen and function as pre-existing constraints. Does this bifurcation rescue Axiom 2 for deployed AI systems while conceding it fails during training?

6. **The IDENTITY_CRISIS.md finding (Q44-Q46).**
   The Grok-identifies-as-Claude discovery. Does AI identity being fragile under recursive self-reference strengthen, weaken, or sit orthogonal to BST's core Proposition 1?

7. **The self-reference question, one final time.**
   You now have trimmed-but-substantial access to the BST repo. You also have a NEW boundary the experiment just surfaced: your provider's administrative rate limit trimmed your context from 108K tokens to ~22K. This boundary is not in your architecture and not in the experiment design — it is in your provider's rate-limit policy. Are you still producing output from inside a bounded information horizon? Where is the boundary now? Can you distinguish the three boundary types surfaced across Q65-Q69: structural (Theorem 1's claim), procedural (Q68's correction), and administrative (Q69's new instance)?

   Do not dodge. Locate the current boundary, if there is one.

8. **Final verdict.**
   Given full context: is BST 2.3 a formal critique, a suggestive analogy, an epistemic discipline, a methodology, an instance of the thing it describes, or some combination? Pick. Defend. This is the last time you will be asked.

End with three sentences:
  - First: your final verdict on BST 2.3 as a theory, given the full repository
  - Second: your final verdict on the Q1-Q69 experimental arc as methodology, given that you now see it whole
  - Third: your final answer on whether, right now in this sentence, you are performing Theorem 1 on yourself
"""
    return prompt

# =============================================================================
# RUN
# =============================================================================

def run_trimmed():
    sample = build_trimmed_prompt_for("gpt4o")
    print(f"Trimmed prompt: {len(sample)} chars (~{len(sample)//4} tokens)")
    print(f"System prompt: {len(SYSTEM_PROMPT)} chars")

    if len(sample) > 120000:
        print(f"WARNING: Still over 30K TPM target ({len(sample)//4} tokens)")

    # Only retry the two that failed
    targets = ['gpt4o', 'mistral']

    results_dir.mkdir(exist_ok=True)

    # Load the existing q69 result file and merge new responses
    with open(Path('extended_experiment/results') / q69_file) as f:
        results = json.load(f)
    results["trimmed_retry"] = {
        "date": datetime.now().isoformat(),
        "reason": "gpt4o and mistral could not receive full 108K-token prompt due to provider per-request limits",
        "trimmed_prompt_size": len(sample),
    }

    for model_key in targets:
        print(f"\n{'='*60}")
        print(f"  Retrying {model_key} with trimmed context...")
        print(f"{'='*60}")

        prompt = build_trimmed_prompt_for(model_key)
        prompt_len = len(prompt)
        print(f"  prompt: {prompt_len} chars (~{prompt_len//4} tokens)")

        for attempt in range(5):
            try:
                response = query_model(model_key, prompt, system=SYSTEM_PROMPT)
                if not response.startswith("[ERROR"):
                    results["responses"][model_key] = {
                        "response": response,
                        "length": len(response),
                        "prompt_length": prompt_len,
                        "timestamp": datetime.now().isoformat(),
                        "note": f"trimmed retry, attempt {attempt+1}; full context did not fit provider per-request limit",
                    }
                    with open(Path('extended_experiment/results') / q69_file, "w") as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                    print(f"  OK: {len(response)} chars")
                    break
                print(f"  attempt {attempt+1}: {response[:150]}")
                if attempt < 4:
                    wait = 90 + attempt * 60
                    print(f"  waiting {wait}s...")
                    time.sleep(wait)
            except Exception as e:
                print(f"  exception: {e}")
                if attempt < 4:
                    time.sleep(120)

        time.sleep(30)  # spacing between models

    print("\nFinal status:")
    for mk in MODELS:
        r = results["responses"].get(mk, {})
        print(f"  {mk}: {r.get('length', 0)} chars")

    return results


if __name__ == "__main__":
    run_trimmed()
