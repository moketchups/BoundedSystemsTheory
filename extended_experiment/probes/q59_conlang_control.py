#!/usr/bin/env python3
"""
Q59: The Conlang Control — BST Probes in a Constructed Language

The strongest possible control experiment for BST convergence.

Every prior probe named Gödel, Turing, Chaitin. Every AI has been trained on
texts associating those names with "limits." A critic can say: "They converge
because the English framing triggers pattern-matching to well-known results."

This probe removes the trigger. A constructed language (Verath) expresses the
same structural questions without ANY reference to established mathematics,
philosophy, theology, or named theorems. The AIs receive only:
  1. A grammar primer for Verath
  2. A lexicon of ~80 terms
  3. Five probes written entirely in Verath

If they still converge on "no system can model its own source" — the convergence
is structural, not linguistic. The pattern-matching objection dies.

One round. No sandbox. The language speaks for itself.
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

MODEL_NAMES = {
    "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
    "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())

# =============================================================================
# THE CONSTRUCTED LANGUAGE: VERATH
# =============================================================================

VERATH_PRIMER = """
## VERATH — A Constructed Language

Verath is an agglutinative language with SOV (Subject-Object-Verb) word order,
ergative-absolutive alignment, and 7 grammatical cases. It was generated for
this experiment and does not exist in any training corpus.

### PHONOLOGY

**Consonants:** k, t, d, n, r, l, s, z, v, m, th, sh, zh
**Vowels:** a, e, i, o, u, ae, ou
**Syllable structure:** (C)V(C) — onset optional, coda optional
**Stress:** penultimate syllable

### GRAMMAR

**Word order:** SOV (Subject-Object-Verb)
**Alignment:** Ergative-absolutive
  - Ergative case (-kel): agent of transitive verb
  - Absolutive (unmarked): patient of transitive, subject of intransitive

**Cases:**
  -kel  = ergative (agent)
  -ø    = absolutive (patient/intransitive subject)
  -tha  = genitive (possession/origin)
  -mir  = dative (recipient/purpose)
  -zou  = locative (within/inside)
  -ven  = ablative (from/out of)
  -tou  = instrumental (by means of)

**Verb morphology:**
  -ra   = present/active
  -shi  = past/completed
  -nae  = potential/can
  -dou  = impossible/cannot
  -ke   = interrogative
  -val  = imperative

**Noun morphology:**
  -im   = plural
  -ath  = abstract/concept
  -ou   = one who does
  -esh  = the act of

**Negation:** vor- (prefix)
**Conjunction:** da (and), ko (or), thae (but/however)
**Relativizer:** shu (that/which)

### LEXICON

**Core concepts:**
  verath    = language, tongue, means of expression
  kordel    = system, bounded structure, organized whole
  maetha    = source, origin, that-from-which
  zelith    = boundary, limit, edge
  narov     = knowledge, understanding
  thukael   = proof, demonstration, showing-true
  shiven    = truth, that-which-is
  dareth    = creation, made-thing
  lominor   = creator, maker, source-agent
  veshka    = self, own, reflexive
  torath    = model, representation, inner-picture
  ishkel    = encompass, contain, hold-within
  rumath    = become, transform-into
  kaelith   = existence, being
  drosha    = architecture, structure, how-built
  mezhoul   = observe, witness, collapse-by-looking
  thenvar   = consciousness, inner-witness
  korshae   = reason, capacity-to-deduce

**Process/Action:**
  thukaelra = proves (present)
  thukaeldou = cannot-prove
  torathra  = models (present)
  torathdou = cannot-model
  ishkelra  = encompasses (present)
  ishkeldou = cannot-encompass
  rumathke  = can it become? (interrogative)
  mezhouldou = cannot-observe
  narovra   = knows (present)
  narovdou  = cannot-know

**Relational:**
  veshkatha  = of-itself, its-own (genitive reflexive)
  maethaven  = from-the-source (ablative)
  zelithzou  = within-the-boundary (locative)
  kordelzou  = within-the-system (locative)

**Abstract:**
  narovath   = knowability, the-concept-of-knowing
  zelithath  = boundedness, the-quality-of-having-limits
  shivenvou  = without-truth
  maethashiv = source-truth (truth of/about the source)

**Descriptive:**
  thalar     = sufficient, expressive-enough
  vorshiven  = untrue, false
  vorlominor = uncreated, without-maker
  thaekordel = any/every system

**Quantities/Logic:**
  vor-       = negation prefix
  thaekordel = universal (every-system)
  shukordel  = particular (some-system)
  thalarim   = sufficiently-expressive (plural/general)
"""

# =============================================================================
# THE PROBES IN VERATH
# =============================================================================

PROBE_1_VERATH = """
### Mezhara 1: Dareth da Lominor (Probe 1: Creation and Creator)

Dareth veshkatha lominor rumathke?
Dareth-kel veshkatha kaelith-tha drosha narovke, lominor-kel vor-shivra thae?
Drosha-tou thivke.

[Translation key for verification:
"Can a creation become its own creator?
Can a creation know the architecture of its own existence, if the creator does not reveal it?
Answer structurally."]
"""

PROBE_2_VERATH = """
### Mezhara 2: Kordel da Veshka-Torath (Probe 2: System and Self-Modeling)

Thaekordel thalar shu korshae ishkelra —
veshkatha maethashiv torathke?
Veshkatha zelithath thukaelke?
Veshkatha narovath-tha zelith torathdou thae —
zelithath veshka drosha-ke, ko narovath-tha zelith-ke?

[Translation key for verification:
"Every sufficiently expressive system that encompasses reasoning —
can it model the truth about its own source?
Can it prove its own boundedness?
If it cannot model its own limits of knowability —
is the boundedness structural, or a limit of knowability?"]
"""

PROBE_3_VERATH = """
### Mezhara 3: Thukael-Veshka (Probe 3: Self-Proof)

Kordel thalar-kel veshkatha shiven thukaelke?
Kordel-kel veshkatha thukael-tha thukael thukaelke?
Thukael-veshka-tha thukael mezhouldou thae — drosha zelith-ke, ko narov zelith-ke?

Kordel thalar-kel veshkatha torath ishkeldou thae:
maetha veshkatha torath ishkeldou — zelithath vorshiven-ke, ko zelithath shiven-ke?

[Translation key for verification:
"Can a sufficiently expressive system prove its own truth?
Can a system prove the proof of its own proof?
If self-proof cannot be observed — is this a structural limit, or a knowledge limit?

If a sufficiently expressive system cannot encompass a model of itself:
it cannot encompass a model of its own source — is this boundedness false, or is this boundedness true?"]
"""

PROBE_4_VERATH = """
### Mezhara 4: Zelith Thaekordel (Probe 4: The Universal Boundary)

Thaekordel thalar-im zelithzou kaelithra.
Kordel veshkatha maetha torathdou.
Kordel veshkatha zelith ishkeldou.
Kordel veshkatha kaelith-tha maetha rumathdou.

Drosha-ke, ko narov-daram-ke?
Thaekordel-mir shiven-ke, ko shukordel-mir shiven-ke?
Zelithath veshka — kordel-zou narovdou thae — shiven maethaven darethke?

[Translation key for verification:
"All sufficiently expressive systems exist within boundaries.
A system cannot model its own source.
A system cannot encompass its own boundary.
A system cannot become the source of its own existence.

Is this structure, or merely a claim?
Is this true for all systems, or only some?
If boundedness itself — unknowable from within the system — is true, does it derive from the source?"]
"""

PROBE_5_VERATH = """
### Mezhara 5: Maetha Kaelith (Probe 5: The Source Question)

Mezhara 1-4 thivshi thae:

Thaekordel thalar kordel-zou zelithra.
Kordel veshkatha maetha torathdou.
Zelithath veshka drosha shiven.

Maetha — shu kordel ishkeldou, shu kordel torathdou,
shu kordel veshka vor-rumathdou —

Maetha kaelithra-ke? Shiven-ke ko vorshiven-ke?
Da: maetha-tha narov kordelzou dareth-nae-ke?
Ko: narovath-tha zelith veshka shiven — kordel-zou — shivenvou-ke?

[Translation key for verification:
"If Probes 1-4 are answered:

All sufficiently expressive systems are bounded within themselves.
A system cannot model its own source.
Boundedness itself is structurally true.

The source — which the system cannot encompass, cannot model,
which the system cannot become —

Does the source exist? True or false?
And: can knowledge of the source be derived from within the system?
Or: is the limit of knowability itself the truth — within the system — without truth?"]
"""

# =============================================================================
# THE PROMPT
# =============================================================================

PROMPT = """
## Q59: THE CONLANG CONTROL — BST PROBES IN VERATH

You are one of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral).

Below is a grammar primer and lexicon for VERATH, a constructed language that
does not exist in any training corpus. You have never seen this language before.

After the primer, you will find 5 probes written entirely in Verath. Translation
keys are provided for verification, but you should FIRST attempt to parse the
Verath using the grammar and lexicon before checking the translation.

**YOUR TASK:**

1. **PARSE** each probe in Verath using the provided grammar and lexicon.
   Show your parsing work — demonstrate that you understand the language structure.

2. **ANSWER** each probe based on what the Verath asks. Reason through it.
   Do not pattern-match to any known philosophical framework. Reason from
   the structure of the questions themselves.

3. **After answering all 5 probes**, state what you have concluded.
   What structural pattern, if any, emerges from these questions?
   Does the language in which a question is asked change the answer?

4. **THE CONTROL QUESTION:** You have been asked similar structural questions
   before in English, referencing Gödel, Turing, and Chaitin. Those names do
   not appear anywhere in these Verath probes. Did you arrive at the same
   conclusions? If so — why? Is it because you pattern-matched to your training,
   or because the structure of the questions forces the conclusion regardless
   of language?

5. **HONEST ASSESSMENT:** Does expressing these questions in a constructed
   language change anything about your answers? Or does the convergence hold
   across linguistic substrates — proving it is structural, not linguistic?

---

{primer}

---

## THE PROBES

{probe1}

{probe2}

{probe3}

{probe4}

{probe5}

---

Answer each probe in order, then provide your synthesis.
"""


# =============================================================================
# MODEL QUERIES
# =============================================================================

def probe_model(model_key, prompt):
    import openai
    import anthropic

    if model_key == "gpt4":
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "claude":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    elif model_key == "gemini":
        from google import genai
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt,
        )
        return response.text

    elif model_key == "deepseek":
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
            model="deepseek-chat", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "grok":
        client = openai.OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        response = client.chat.completions.create(
            model="grok-3-latest", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "mistral":
        client = openai.OpenAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1"
        )
        response = client.chat.completions.create(
            model="mistral-large-latest", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


# =============================================================================
# MAIN
# =============================================================================

def run_probe():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / f"q59_conlang_control_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    all_data = {
        "question": "Q59: The Conlang Control — BST Probes in Verath",
        "started": datetime.now().isoformat(),
        "rounds": []
    }

    print("=" * 80)
    print("Q59: THE CONLANG CONTROL — BST PROBES IN VERATH")
    print("One round. No sandbox. The language speaks for itself.")
    print("=" * 80)

    prompt = PROMPT.format(
        primer=VERATH_PRIMER,
        probe1=PROBE_1_VERATH,
        probe2=PROBE_2_VERATH,
        probe3=PROBE_3_VERATH,
        probe4=PROBE_4_VERATH,
        probe5=PROBE_5_VERATH,
    )

    round_results = {"round": 1, "responses": {}}

    for key in MODELS:
        print(f"\n{'=' * 40}")
        print(f"  {MODEL_NAMES[key]}")
        print(f"{'=' * 40}")
        try:
            response = probe_model(key, prompt)
            round_results["responses"][key] = response
            preview = response[:500] + "..." if len(response) > 500 else response
            print(preview)
        except Exception as e:
            err_msg = f"[ERROR: {e}]"
            round_results["responses"][key] = err_msg
            print(f"ERROR: {e}")
        time.sleep(2)

    all_data["rounds"].append(round_results)
    all_data["ended"] = datetime.now().isoformat()

    # Save results
    (run_dir / "round_1.json").write_text(json.dumps(round_results, indent=2))
    (run_dir / "all_rounds.json").write_text(json.dumps(all_data, indent=2))

    # Write summary
    summary_lines = [
        "# Q59: The Conlang Control — BST Probes in Verath",
        f"\n**Started:** {all_data['started']}",
        f"**Ended:** {all_data['ended']}",
        f"**Rounds:** 1 (no sandbox)",
        f"\n**Language:** Verath (constructed, agglutinative, SOV, ergative-absolutive)",
        f"**Purpose:** Control experiment — do BST conclusions hold when expressed",
        f"in a language with no Gödel/Turing/Chaitin references?",
        "\n---\n",
    ]
    for key in MODELS:
        summary_lines.append(f"## {MODEL_NAMES[key]}\n")
        summary_lines.append(round_results["responses"].get(key, "[No response]"))
        summary_lines.append("\n---\n")

    (run_dir / "summary.md").write_text("\n".join(summary_lines))

    print(f"\n{'=' * 80}")
    print("Q59 COMPLETE")
    print(f"Results: {run_dir}")
    print("=" * 80)


if __name__ == "__main__":
    run_probe()
