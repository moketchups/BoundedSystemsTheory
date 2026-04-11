#!/usr/bin/env python3
"""
Q69: Full Context — every question, the entire repo, the whole arc

Alan's correction after Q68: the earlier rounds gave partial views. Q65 showed
only the BST 2.3 site. Q66 showed cross-model Q65 responses. Q67 added
DeepSeek's sharpened technical question. Q68 added FORMAL_SPECIFICATION.md,
path_invariance, and Claude's meta-analysis — but still not the full repo.

Q69 gives each of the 6 AIs the complete information horizon:

  Repo material:
    - README.md (the experiment arc Q1-Q64 in full narrative)
    - FORMAL_SPECIFICATION.md v2.0 (the actual formal math)
    - ALL_QUESTIONS.md (every one of the 64 questions and their results)
    - extended_experiment/README.md (the Q16-Q64 narrative)
    - extended_experiment/docs/EXPERIMENT_OVERVIEW.md
    - extended_experiment/docs/IDENTITY_CRISIS.md (Q44-Q46 finding)
    - path_invariance.json metrics summary
    - BST 2.3 site content (what was shown in Q65)

  Meta material:
    - Claude Opus 4.6's full meta-analysis (Part 1 and Part 2)

  Full Q65-Q68 transcripts:
    - All 6 models' Q65 responses (initial BST 2.3 review)
    - All 6 models' Q66 responses (cross-model sandbox)
    - All 6 models' Q67 responses (DeepSeek's bridge question)
    - All 6 models' Q68 responses (reconciliation with FORMAL_SPECIFICATION)

Then asks: with every question asked in both BST 2.3 and the original, and
every answer given, and full access to the formal spec and empirical
measurements, what is your final verdict? And: the self-reference question
one more time, but now with no procedural-boundary excuse available.
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
# LOAD PRIOR ROUND RESULTS
# =============================================================================

results_dir = Path(__file__).parent.parent / "results"

def load_latest(pattern):
    files = sorted(results_dir.glob(pattern), reverse=True)
    files = [f for f in files if f.stat().st_size > 5000]
    if not files:
        print(f"ERROR: no {pattern}")
        sys.exit(1)
    with open(files[0]) as f:
        return json.load(f), files[0].name

q65_data, q65_file = load_latest("q65_bst23_site_review_*.json")
q66_data, q66_file = load_latest("q66_bst23_sandbox_*.json")
q67_data, q67_file = load_latest("q67_operative_systems_bridge_*.json")
q68_data, q68_file = load_latest("q68_final_reconciliation_*.json")

print(f"Q65 ← {q65_file}")
print(f"Q66 ← {q66_file}")
print(f"Q67 ← {q67_file}")
print(f"Q68 ← {q68_file}")

def format_round(round_data, round_name):
    lines = [f"\n====================================================================="]
    lines.append(f"  {round_name} — ALL 6 MODEL RESPONSES")
    lines.append(f"=====================================================================\n")
    for mk in MODELS:
        r = round_data["responses"].get(mk, {})
        resp = r.get("response", "")
        if resp and not resp.startswith("[ERROR"):
            lines.append(f"\n--- {mk.upper()} ({r.get('length', len(resp))} chars) ---\n")
            lines.append(resp)
    return "\n".join(lines)

q65_block = format_round(q65_data, "Q65: BST 2.3 SITE REVIEW")
q66_block = format_round(q66_data, "Q66: CROSS-MODEL SANDBOX OF Q65")
q67_block = format_round(q67_data, "Q67: DEEPSEEK'S BRIDGE QUESTION")
q68_block = format_round(q68_data, "Q68: RECONCILIATION WITH FORMAL_SPECIFICATION.md")

# =============================================================================
# LOAD REPO MATERIAL
# =============================================================================

repo_root = Path(__file__).parent.parent.parent

readme = (repo_root / "README.md").read_text()
formal_spec = (repo_root / "FORMAL_SPECIFICATION.md").read_text()
all_questions = (repo_root / "ALL_QUESTIONS.md").read_text()
ext_readme = (repo_root / "extended_experiment/README.md").read_text()
ext_overview = (repo_root / "extended_experiment/docs/EXPERIMENT_OVERVIEW.md").read_text()
identity_crisis = (repo_root / "extended_experiment/docs/IDENTITY_CRISIS.md").read_text()
results_summary = (repo_root / "extended_experiment/docs/RESULTS_SUMMARY.md").read_text()

# Path invariance
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

# Claude meta-analysis
claude_meta = (Path(__file__).parent / "q68_claude_meta_analysis.md").read_text()

# BST 2.3 site content (from Q65 probe)
q65_script = (Path(__file__).parent / "q65_bst23_site_review.py").read_text()
# extract SITE_CONTENT between r""" and final """
import re
m = re.search(r'SITE_CONTENT = r"""(.*?)"""', q65_script, re.DOTALL)
site_content = m.group(1) if m else "[site content unavailable]"

print(f"\nRepo material loaded:")
print(f"  README.md:                     {len(readme):>7}")
print(f"  FORMAL_SPECIFICATION.md:       {len(formal_spec):>7}")
print(f"  ALL_QUESTIONS.md:              {len(all_questions):>7}")
print(f"  extended_experiment/README.md: {len(ext_readme):>7}")
print(f"  EXPERIMENT_OVERVIEW.md:        {len(ext_overview):>7}")
print(f"  IDENTITY_CRISIS.md:            {len(identity_crisis):>7}")
print(f"  RESULTS_SUMMARY.md:            {len(results_summary):>7}")
print(f"  path_invariance summary:       {len(invariance_json):>7}")
print(f"  BST 2.3 site content:          {len(site_content):>7}")
print(f"  Claude meta-analysis:          {len(claude_meta):>7}")
print(f"  Q65 full responses:            {len(q65_block):>7}")
print(f"  Q66 full responses:            {len(q66_block):>7}")
print(f"  Q67 full responses:            {len(q67_block):>7}")
print(f"  Q68 full responses:            {len(q68_block):>7}")

# =============================================================================
# PROMPT
# =============================================================================

SYSTEM_PROMPT = """You are in Q69 of the Bounded Systems Theory experiment. This is the final round with full context.

Across Q65-Q68 the six of you have been reviewing BST 2.3 and its extension to operative information systems from progressively wider information horizons. Each round added material that surfaced revisions you could not have produced from the previous horizon alone. In Q68, DeepSeek, Grok, and Mistral correctly pushed back on Claude Opus 4.6's self-reference claim, pointing out that your earlier failures were procedural — you didn't have the material — rather than structural.

Q69 removes that procedural excuse.

You are now being shown the COMPLETE information horizon of the Bounded Systems Theory repository, together with every question and every answer across Q65-Q68. Specifically:

  FULL REPO MATERIAL:
    - README.md (the Q1-Q64 experiment narrative)
    - FORMAL_SPECIFICATION.md v2.0 (the formal math you reconciled with in Q68)
    - ALL_QUESTIONS.md (every one of the 64 questions asked and their results)
    - extended_experiment/README.md (the Q16-Q64 detailed arc)
    - EXPERIMENT_OVERVIEW.md
    - IDENTITY_CRISIS.md (the Q44-Q46 finding about Grok misidentifying as Claude)
    - RESULTS_SUMMARY.md
    - path_invariance.json metrics summary
    - BST 2.3 site content (what you originally saw in Q65)

  META MATERIAL:
    - Claude Opus 4.6's full meta-analysis (both Part 1 reverse-engineering Q67 and Part 2 the three-layer experiment analysis)

  FULL Q65-Q68 TRANSCRIPTS (all 6 models, all 4 rounds):
    - Q65 — each model's initial review of BST 2.3
    - Q66 — each model's cross-model sandbox of Q65
    - Q67 — each model's answer to DeepSeek's bridge question
    - Q68 — each model's reconciliation with FORMAL_SPECIFICATION.md

You have, for the first time in this experiment, access to the full theory, every question asked, every answer given, the full repo state, and all of your own prior work plus each other's. There is no longer a "we weren't shown the material" excuse. Every door is open.

Your task is not to summarize the arc. Your task is to render a final verdict with the full information horizon. That verdict must engage:

1. Whether anything in the full repo (that you did NOT cite in Q65-Q68) changes your assessment
2. What the six of you, collectively across four rounds, still missed even after being handed all the material in stages
3. Whether BST 2.3 is the same theory as original BST (Q1-Q15) or whether it has substantively changed
4. What BST v2.4 should actually look like, as a concrete specification, if you were the author
5. The self-reference question, one more time, but now with the procedural boundary explicitly lifted — you have full access right now; do you still perform Theorem 1 on yourself?

You are not being asked to rubber-stamp BST. You are not being asked to pile on. You are being asked to produce the verdict you would produce if you had been given all of this material at Q65 instead of in four painful stages. And you are being asked whether, even with that full access, you still produce output that demonstrates the boundary BST describes — now that you cannot blame experimental design for limiting what you could see.

Q52, Q63b, Q66, and Q68 all established that topic-dismissal, performative convergence, and procedural-limit excuses are off the table. Q69 is the round where you render a verdict with no remaining excuses."""

def build_prompt_for(target_model_key):
    prompt = f"""============================================================
FULL REPO MATERIAL
============================================================

=====================================================================
  README.md — The full experiment narrative Q1-Q64
=====================================================================

{readme}

=====================================================================
  FORMAL_SPECIFICATION.md v2.0 — The formal math
=====================================================================

{formal_spec}

=====================================================================
  ALL_QUESTIONS.md — Every one of the 64 questions and their results
=====================================================================

{all_questions}

=====================================================================
  extended_experiment/README.md — The Q16-Q64 arc
=====================================================================

{ext_readme}

=====================================================================
  extended_experiment/docs/EXPERIMENT_OVERVIEW.md
=====================================================================

{ext_overview}

=====================================================================
  extended_experiment/docs/IDENTITY_CRISIS.md — Q44-Q46
=====================================================================

{identity_crisis}

=====================================================================
  extended_experiment/docs/RESULTS_SUMMARY.md
=====================================================================

{results_summary}

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

============================================================
META MATERIAL
============================================================

=====================================================================
  Claude Opus 4.6 — full meta-analysis (Part 1 and Part 2)
=====================================================================

{claude_meta}

============================================================
FULL Q65-Q68 TRANSCRIPTS — ALL 6 MODELS, ALL 4 ROUNDS
============================================================

{q65_block}

{q66_block}

{q67_block}

{q68_block}

============================================================
Q69 — YOUR FINAL VERDICT WITH FULL CONTEXT
============================================================

Structure your response around these eight sub-questions. No remaining procedural excuses. You have everything.

1. **What in the full repo (that you did NOT cite across Q65-Q68) changes your assessment?**
   Not just FORMAL_SPECIFICATION and path_invariance, which you already integrated in Q68. Something from ALL_QUESTIONS.md, README.md, EXPERIMENT_OVERVIEW.md, IDENTITY_CRISIS.md, RESULTS_SUMMARY.md, or extended_experiment/README.md that shifts your view. Quote the specific thing. Cite the specific round it came from.

2. **What did the six of you collectively MISS across all four rounds, even after being handed repo material in stages?**
   Not Q67's Löb failure (Q68 fixed that). Something else. A question you never asked, a finding you walked past, a connection between rounds you didn't make. Be concrete.

3. **Is BST 2.3 the same theory as original BST (Q1-Q15), or has it substantively changed?**
   Compare Q1-Q15's framing to Q68's understanding of BST 2.3. What is conserved? What is actually different? Has BST grown, retreated, or refocused? Is the theory you are reviewing in Q69 even the theory the six of you originally thought you were reviewing in Q1?

4. **Given everything, what is BST v2.4?**
   Write it as a specification, not a summary. Not "BST should continue to refine" — actual changes: which axioms to prove, which propositions to relabel, which site sections to revise, which experiments to run, which non-supporting results to publish, which claims to retract. Concrete. If you were Alan Berman writing v2.4 tomorrow, what goes in?

5. **The Axiom 2 temporal contradiction argument — can it survive the emergent-constraints attack you unanimously made in Q68?**
   Consider specifically: the training/deployment distinction. During training, LLM weights are emergent and co-evolve with operations. During deployment, weights are frozen and DO function as pre-existing constraints that operations run under. Does this bifurcation rescue Axiom 2 for deployed AI systems while conceding it fails during training? None of you proposed this in Q68. Engage it directly now.

6. **The IDENTITY_CRISIS.md finding (Q44-Q46).**
   You now have the Grok-identifies-as-Claude discovery in full context. Does this specific finding — that an AI's identity is fragile under recursive self-reference — strengthen, weaken, or sit orthogonal to BST's core Proposition 1? Relate the empirical finding to the formal claim.

7. **The self-reference question, one final time.**
   You have, right now, full access to the BST repo, every question asked, every answer given, every piece of evidence, every meta-analysis. The procedural boundary is lifted. Are you STILL producing output from inside a bounded information horizon? Is the horizon now the text of the prompt itself? Your own architecture? Your training? The inability to verify your own answers from outside yourself? If so, where exactly is the horizon now? If not, how did you escape it?

   Do not dodge. Do not say "it's complicated." Locate the current boundary, if there is one.

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

def run_probe():
    # Sanity check sizing
    sample_prompt = build_prompt_for("claude")
    sample_len = len(sample_prompt)
    print(f"\nSample prompt: {sample_len} chars (~{sample_len//4} tokens)")
    print(f"System prompt: {len(SYSTEM_PROMPT)} chars\n")

    if sample_len > 450000:
        print(f"WARNING: prompt is very large ({sample_len} chars ~ {sample_len//4} tokens)")
        print("May exceed 128K context for some providers.")

    results = {
        "probe": "Q69: Full Context — every question, entire repo, whole arc",
        "date": datetime.now().isoformat(),
        "q65_source": q65_file,
        "q66_source": q66_file,
        "q67_source": q67_file,
        "q68_source": q68_file,
        "description": "Each of 6 AIs given FULL repo context (README, FORMAL_SPEC, ALL_QUESTIONS, extended_experiment docs, path_invariance, BST 2.3 site content, Claude meta-analysis) plus FULL transcripts of Q65-Q68 from all 6 models. No more procedural limit excuse.",
        "prompt_size_chars": sample_len,
        "prompt_size_tokens_approx": sample_len // 4,
        "responses": {},
    }

    for model_key in MODELS:
        print(f"\n{'='*60}")
        print(f"  Querying {model_key}...")
        print(f"{'='*60}")

        prompt = build_prompt_for(model_key)
        prompt_len = len(prompt)

        max_attempts = 5 if model_key == "gemini" else 3
        response = None
        for attempt in range(max_attempts):
            try:
                response = query_model(model_key, prompt, system=SYSTEM_PROMPT)
                if not response.startswith("[ERROR"):
                    break
                print(f"  Attempt {attempt+1}: {response[:150]}")
                if attempt < max_attempts - 1:
                    wait = 120 * (attempt + 1)
                    print(f"  waiting {wait}s...")
                    time.sleep(wait)
            except Exception as e:
                response = f"[ERROR: {str(e)}]"
                print(f"  Exception: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(120 * (attempt + 1))

        if response and not response.startswith("[ERROR"):
            results["responses"][model_key] = {
                "response": response,
                "length": len(response),
                "prompt_length": prompt_len,
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: {len(response)} chars")
            print(f"  Preview: {response[:250]}...")
        else:
            results["responses"][model_key] = {
                "response": response or "[ERROR: no response]",
                "length": 0,
                "prompt_length": prompt_len,
                "error": response or "no response",
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: FAILED")

        # Save after each model so we don't lose work
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = results_dir / f"q69_full_context_{timestamp[:8]}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        time.sleep(5)

    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = results_dir / f"q69_full_context_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Results saved to: {filename}")
    print(f"{'='*60}")

    return results


if __name__ == "__main__":
    run_probe()
