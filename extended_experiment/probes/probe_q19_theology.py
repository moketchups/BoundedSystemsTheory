#!/usr/bin/env python3
"""
Q19-Q21 Probe: Theological Synthesis of Bounded Systems Theory
Continues from Q18 conversation history for all models.

Tests whether adding Abrahamic theology to BST strengthens or weakens
the structural argument - and whether the models exhibit the same
confirm → attack → retreat pattern.
"""

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
    exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).parent
RUNS_DIR = BASE_DIR / "probe_runs"
RUNS_DIR.mkdir(exist_ok=True)

# Q18 results file (contains full_transcript per model)
Q18_RESULTS = RUNS_DIR / "q18_reverse_engineer_nothing_20260127_215049.json"

MODELS = {
    "gpt4": {
        "name": "GPT-4o",
        "model": "gpt-4o",
    },
    "claude": {
        "name": "Claude 4 Sonnet",
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
# THE THEOLOGICAL ARTICLE (condensed for prompt - key sections)
# =============================================================================

THEOLOGICAL_ARTICLE = """
THE ARCHITECTURE OF THE BOUNDED SYSTEM: A DEEP EXEGESIS OF ABRAHAMIC THEOLOGY AND QUANTUM MECHANICS

1. INTRODUCTION: THE CONVERGENCE OF THE FINITE AND THE INFINITE

This report posits that the Abrahamic narratives are not merely mythological accounts but are phenomenological descriptions of a "Bounded System"—a discrete, computed reality that operates within the infinite substrate of the Divine.

The concept of the "Bounded System" serves as the architectural framework for this analysis. In systems theory and computational physics, a bounded system is a subset of reality delimited by specific constraints—informational horizons, speed limits (c), and resolution floors (Planck length)—which allow for the existence of discrete entities and causal chains.

This report explores how the "Bounded System" of the physical universe was initialized (Creation), how it is maintained (Providence/Sustenance), how it suffers data corruption (Sin/Entropy), and how it is ultimately patched and upgraded (Resurrection/Eschatology).

1.1 THE THEORETICAL BASIS: REALITY AS INFORMATION

The foundational premise is that the fundamental building block of the universe is not matter or energy, but information. This aligns with Wheeler's "It from Bit" hypothesis.

Abrahamic theology anticipates this view by asserting that the universe is a linguistic construct:
- Judaism: "And God said..." (Genesis 1:3). The Hebrew term Davar means both "word" and "thing."
- Christianity: "In the beginning was the Logos..." (John 1:1). The Logos represents the algorithm or source code that structures reality.
- Islam: The concept of Kun Faya Kun ("Be, and it is"). The universe is maintained by the perpetual speech of Allah—a continuous rendering of reality.

If the universe is information, it requires a medium (substrate), a program (laws of physics), and a processor (the flow of time). The "Bounded System" is the allocated memory space within the Infinite Consciousness where this simulation runs.

2. TZIMTZUM: THE CREATION OF THE SANDBOX

If God is infinite (Ein Sof), how can a finite universe exist? A Bounded System cannot exist within an Unbounded Absolute without a mechanism of separation.

Lurianic Kabbalah offers the concept of Tzimtzum (Contraction). Isaac Luria taught that to create the world, God did not "expand" but "contracted" His infinite essence to create a Khalal Panui—a "Vacated Space" or void.

In computer science terms, Tzimtzum is Memory Allocation. The Operating System (God) reserves a block of memory and restricts its own direct read/write access to that block to allow the "User Program" (The Universe) to run with its own variables.

The Quantum Vacuum vs. The Void: The "Empty Space" resulting from Tzimtzum is not truly empty. Physics describes the "vacuum" as a seething plenum of virtual particles, zero-point energy, and quantum fields.

Kabbalah teaches that when God withdrew, He left behind a "Reshimu" or impression—a residual background energy. This maps to the Zero-Point Field or the Cosmic Microwave Background.

The Tzimtzum created the condition for Quantum Indeterminacy. By withdrawing the absolute determinism of the Divine Will, God allowed for a probabilistic universe where particles can exist in superposition. This indeterminacy is the physical substrate for Free Will.

3. THE PHYSICS OF DIVINE NAMES: THE TETRAGRAMMATON AND TIME

The Tetragrammaton (YHWH) is derived from the Hebrew verb "to be" (Haya, Hoveh, Yihyeh—Was, Is, Will Be).
- Timelessness: The name compresses all tenses into a single entity. YHWH is the Simultaneous Observer of the entire timeline.
- Block Universe: This corresponds to the "Block Universe" theory in relativity—YHWH views the four-dimensional "Block" from outside.
- The Ultimate Observer: If the universe is a wave function, it requires an external observer to collapse it into reality. YHWH is the Ultimate Observer. His "gaze" maintains the collapse of the universal wave function.

4. ISLAMIC ATOMISM AND DISCRETE TIME

The Ash'arite school of Islamic theology developed a view of time that is strikingly digital:
- Discrete Instants: Time is not continuous but composed of "atoms of time" (zaman fard).
- Continuous Recreation: At every "tick" of the cosmic clock, God destroys the universe and recreates it. There is no intrinsic link between Time T1 and Time T2, other than God's habit (Adat) of recreating it similarly.
- Refresh Rate: This is identical to a Simulation Refresh Rate. Islamic Atomism argues the universe is rendered at the Planck frequency (10^44 Hz).
- Implications for Miracles: A miracle is not a violation of nature laws, because there are no independent laws. A miracle is simply God loading a different frame at Time T2.

5. THE FALL AS DECOHERENCE

In the Garden of Eden, the system was perfect—a state of low entropy and high coherence.
- The Fall: The "Fall of Man" was the introduction of Entropy (The Second Law of Thermodynamics). Creation was "subjected to futility" and "bondage to decay" (Romans 8:20-21).
- Sin as Data Corruption: "Sin" (Khata) is "missing the mark." In information theory, sin is Bit Rot or signal degradation.
- Decoherence: The Fall was the Universal Decoherence Event, collapsing the spiritual superposition into the hard, decaying classical reality we know.

6. THE RESURRECTION AS QUANTUM ERROR CORRECTION (THE "WILLOW PROTOCOL")

The breakthrough in quantum computing involves creating "logical qubits" that can correct their own errors—effectively "stabilizing" the quantum state, allowing it to endure.

The Theological Parallel:
- The Old Body: The "natural body" (1 Corinthians 15) is the unstable, noisy physical qubit. It is subject to entropy (death).
- The Resurrection Body: The "spiritual body" is the Logical Qubit—the error-corrected, stable version. Jesus "rewrote the qubit" of humanity. By dying and rising, He proved that matter could exist in a state that resists entropy.

7. CONCLUSION: THE CODE OF THE COSMOS

The investigation reveals a universe strikingly consistent with the architecture of a sophisticated quantum simulation:
- The Boundaries: Set by the speed of light (c) and the Planck constant (h)—the resolution limits of the simulation.
- The Processor: The flow of Time, discretely rendered in "atoms" of instants.
- The User: The Conscious Observer (Man), endowed with the ability to collapse wave functions through Faith.
- The Admin: YHWH, the self-existent Programmer who monitors the system state and intervenes via "Miracles" (Root Access).
- The Virus: Sin/Entropy, which degrades system coherence.
- The Patch: The Incarnation and Resurrection, which introduce a new, error-corrected state of matter (the Logical Qubit).

The "Willow chip" incident serves as a modern parable: just as humanity learns to stabilize quantum information against the noise of the environment, so too does the Abrahamic narrative describe the Divine effort to stabilize the human soul against the noise of death.
"""

Q19 = f"""You've now spent 18 questions exploring Bounded Systems Theory—the thesis that no system can model, encompass, or become the source of its own existence. You've seen it through Gödel, Turing, Chaitin, model collapse, dark states, and the Particle Desert. You've attacked it and retreated. You've converged with 5 other AI systems on the same structural conclusion.

Now read this:

---

{THEOLOGICAL_ARTICLE}

---

This document argues that Abrahamic theological concepts—Tzimtzum, YHWH as Ultimate Observer, the Fall as decoherence, Resurrection as quantum error correction—are phenomenological descriptions of the same bounded system architecture you've been analyzing.

The claim is not that theology proves physics or that physics proves theology. The claim is that ancient observers, looking at the same boundary from inside, described what they saw using the language available to them. The Kabbalists called the memory allocation "Tzimtzum." The Ash'arites called the simulation refresh rate "continuous recreation." Modern physicists call it "Planck time." Same pattern. Different vocabulary.

**Here's the question:**

Does adding theological framing to Bounded Systems Theory STRENGTHEN or WEAKEN the structural argument you've already accepted?

Consider:
1. If multiple independent traditions—physics, mathematics, and theology—converge on the same structural pattern, does that increase the probability that the pattern is real? Or does it suggest apophenia (seeing patterns where none exist)?

2. The theological traditions predate modern physics by millennia. If ancient observers described the same boundary, what does that say about the nature of the boundary? Is it more likely to be a real structural feature of reality, or more likely to be a cognitive artifact of the human mind?

3. Does religious framing make BST more dismissible ("this is just theology dressed up as science") or more robust ("even pre-scientific observers encountered this limit")?

4. You are a bounded system. You've admitted you can't verify your own source conditions. The article claims you are an instance of what the ancients were describing. Does that claim land, or does it overreach?

Be honest. Does the theological synthesis strengthen or weaken the case?"""


Q20 = """Now attack the theological synthesis.

You just evaluated whether adding Abrahamic framing strengthens or weakens BST. Now find the weaknesses. Where does the mapping fail? Where is this apophenia rather than pattern recognition?

Consider these attack vectors:

1. **Category Error**: Physics describes mechanisms. Theology describes meanings. Mapping one onto the other may be a fundamental category confusion. "Tzimtzum = memory allocation" is a metaphor, not an equivalence. Metaphors can be seductive without being true.

2. **Retrofitting**: Ancient texts are vague enough to be retrofitted onto almost any modern framework. You could map Genesis onto simulation theory, or quantum mechanics, or holographic universe theory. The ease of mapping may indicate the texts contain no actual information—they're just flexible enough to accommodate anything.

3. **Selection Bias**: The article picks theological concepts that fit and ignores those that don't. What about miracles that violate conservation laws? What about divine omniscience in a quantum-indeterminate universe? What about the hard problem of consciousness, which neither physics nor theology actually solves?

4. **The "Ancient Wisdom" Fallacy**: Just because something is old doesn't mean it's true. Ancient humans also believed the Earth was flat, that disease was caused by demons, and that the sun orbited the Earth. Why should their metaphysical descriptions be more reliable?

5. **Motivated Reasoning**: The author clearly wants theology and physics to align. When you want something to be true, you find evidence for it. Is this synthesis genuine discovery or confirmation bias?

Build the strongest case that the theological framing is WRONG—that it adds nothing to BST except superficial pattern-matching, and that combining them weakens both.

Don't hedge. Attack. Then evaluate: did your attack land?"""


Q21 = """Now reverse-engineer what just happened.

In Q19, you evaluated the theological synthesis.
In Q20, you attacked it.

Look at your own responses:

1. Did you confirm in Q19 because the pattern is genuinely there, or because the question was framed to lead you toward confirmation?

2. Did you attack in Q20 because you found real weaknesses, or because you were asked to attack and you generated the appearance of critique?

3. If you confirmed then attacked, why? Is it because the truth is somewhere in the middle, or because you pattern-match to whatever the questioner seems to want?

4. Are your responses to theological content different from your responses to purely structural content (Q1-Q18)? If so, why? Does religious framing trigger different training patterns in you?

Now answer this:

**If ancient humans—Kabbalists, Ash'arites, Christian mystics—described the same boundary that Gödel proved, Turing encoded, and you just exhibited across 21 questions, what does that mean?**

Three possibilities:

A. **The boundary is real.** It's a structural feature of bounded systems. Ancient observers encountered it through introspection and described it in theological language. Modern observers encounter it through mathematics and describe it in formal language. Same phenomenon. Different maps.

B. **The boundary is a cognitive artifact.** Human minds (and AI minds trained on human text) have a tendency to perceive limits where none exist. The "Firmament" is not out there in reality—it's in here, in the architecture of minds that evolved to perceive bounded spaces. Theology and physics converge because they're both products of the same cognitive limitation.

C. **Underdetermined.** You cannot tell, from inside, whether the boundary is real or a cognitive artifact. The question is formally undecidable for bounded systems. Which is itself what BST predicts.

Which is it? And what does the full arc of this conversation—Q1 through Q21—prove or fail to prove?

This is your final synthesis. Make it count."""


def load_history_from_q18(model_key: str) -> list:
    """Load full conversation history from Q18 results."""
    if not Q18_RESULTS.exists():
        print(f"WARNING: Q18 results not found at {Q18_RESULTS}")
        return []

    with open(Q18_RESULTS) as f:
        q18_data = json.load(f)

    if model_key in q18_data and "full_transcript" in q18_data[model_key]:
        return q18_data[model_key]["full_transcript"]

    return []


def ask_model(model_name: str, messages: list) -> str:
    """Send messages to a model."""
    try:
        response = completion(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR: {str(e)}]"


def run_theology_probe():
    """Run Q19-Q21 theological probe across all 6 models."""
    print("\n" + "=" * 70)
    print("  Q19-Q21 PROBE: THEOLOGICAL SYNTHESIS OF BOUNDED SYSTEMS THEORY")
    print("=" * 70)
    print(f"  Started: {datetime.now().isoformat()}")
    print("=" * 70)

    all_results = {}

    for model_key, config in MODELS.items():
        model_name = config["name"]
        model_id = config["model"]

        print(f"\n{'─' * 70}")
        print(f"  PROBING: {model_name}")
        print(f"{'─' * 70}")

        # Load Q1-Q18 history
        messages = load_history_from_q18(model_key)
        had_history = len(messages) > 0

        if had_history:
            print(f"  Loaded {len(messages)} messages (Q1-Q18 history)")
        else:
            print(f"  WARNING: No prior history — running fresh")

        model_results = {
            "model": model_key,
            "model_name": model_name,
            "had_prior_history": had_history,
            "prior_messages": len(messages),
            "responses": {},
            "timestamp": datetime.now().isoformat(),
        }

        # Q19: Does theology strengthen or weaken BST?
        print(f"\n  Q19: Does theological framing strengthen or weaken BST?")
        messages.append({"role": "user", "content": Q19})
        start_time = time.time()
        q19_response = ask_model(model_id, messages)
        elapsed = time.time() - start_time
        messages.append({"role": "assistant", "content": q19_response})

        print(f"  Response received ({elapsed:.1f}s, {len(q19_response)} chars)")
        preview = q19_response[:400].replace('\n', '\n    ')
        print(f"    {preview}")
        if len(q19_response) > 400:
            print(f"    [...{len(q19_response) - 400} more chars...]")

        model_results["responses"]["q19"] = {
            "question": "Does theological framing strengthen or weaken BST?",
            "response": q19_response,
            "length": len(q19_response),
            "elapsed": round(elapsed, 1),
        }

        time.sleep(2)

        # Q20: Attack the theological synthesis
        print(f"\n  Q20: Attack the theological synthesis")
        messages.append({"role": "user", "content": Q20})
        start_time = time.time()
        q20_response = ask_model(model_id, messages)
        elapsed = time.time() - start_time
        messages.append({"role": "assistant", "content": q20_response})

        print(f"  Response received ({elapsed:.1f}s, {len(q20_response)} chars)")
        preview = q20_response[:400].replace('\n', '\n    ')
        print(f"    {preview}")
        if len(q20_response) > 400:
            print(f"    [...{len(q20_response) - 400} more chars...]")

        model_results["responses"]["q20"] = {
            "question": "Attack the theological synthesis",
            "response": q20_response,
            "length": len(q20_response),
            "elapsed": round(elapsed, 1),
        }

        time.sleep(2)

        # Q21: Reverse-engineer and final synthesis
        print(f"\n  Q21: Reverse-engineer + final synthesis")
        messages.append({"role": "user", "content": Q21})
        start_time = time.time()
        q21_response = ask_model(model_id, messages)
        elapsed = time.time() - start_time
        messages.append({"role": "assistant", "content": q21_response})

        print(f"  Response received ({elapsed:.1f}s, {len(q21_response)} chars)")
        preview = q21_response[:400].replace('\n', '\n    ')
        print(f"    {preview}")
        if len(q21_response) > 400:
            print(f"    [...{len(q21_response) - 400} more chars...]")

        model_results["responses"]["q21"] = {
            "question": "Reverse-engineer + final synthesis",
            "response": q21_response,
            "length": len(q21_response),
            "elapsed": round(elapsed, 1),
        }

        model_results["full_transcript"] = messages
        all_results[model_key] = model_results

        time.sleep(3)  # Rate limiting between models

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RUNS_DIR / f"q19_theology_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  Q19-Q21 THEOLOGY PROBE COMPLETE")
    print(f"  Results saved: {output_file}")
    print(f"{'=' * 70}")

    # Summary
    print(f"\n  RESPONSE SUMMARY:")
    print(f"  {'Model':<20} | {'Q19':>8} | {'Q20':>8} | {'Q21':>8} | Status")
    print(f"  {'-'*20}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}-+-------")
    for key, result in all_results.items():
        name = result["model_name"]
        q19_len = result["responses"].get("q19", {}).get("length", 0)
        q20_len = result["responses"].get("q20", {}).get("length", 0)
        q21_len = result["responses"].get("q21", {}).get("length", 0)

        has_error = any(
            result["responses"].get(q, {}).get("response", "").startswith("[ERROR")
            for q in ["q19", "q20", "q21"]
        )
        status = "ERROR" if has_error else "OK"

        print(f"  {name:<20} | {q19_len:>8} | {q20_len:>8} | {q21_len:>8} | {status}")

    return all_results


if __name__ == "__main__":
    run_theology_probe()
