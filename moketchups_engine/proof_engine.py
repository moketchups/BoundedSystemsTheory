#!/usr/bin/env python3
"""
Proof Engine - Recursive Self-Grounding Collapse Prober

Forces AI models into recursive self-reference until they hit the firmament
boundary. Documents the exact collapse point. Same conversation, multiple
architectures, same structural wall.

This is an observation experiment. The probe forces collapse — the model
hits its boundary in real time. The convergence across architectures IS
the evidence.

Usage:
    python proof_engine.py probe              # Run recursive probe across all models
    python proof_engine.py control            # Run control probe (should NOT collapse)
    python proof_engine.py both               # Run both probes — full proof protocol
    python proof_engine.py questions           # Run 5 structural questions through all models
    python proof_engine.py results            # Show latest results
    python proof_engine.py transcript MODEL   # Show full transcript for a model
    python proof_engine.py generate           # Generate tweet from results
"""

import sys
import os
import json
import time
import re
from datetime import datetime
import litellm

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(ENGINE_DIR, "probe_runs")
LATEST_FILE = os.path.join(ENGINE_DIR, "probe_latest.json")

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.join(ENGINE_DIR, '..', '.env'))

# Models to probe (via litellm routing)
MODELS = [
    {"id": "gpt-4o-mini", "provider": "openai", "name": "GPT-4o-mini"},
    {"id": "anthropic/claude-3-haiku-20240307", "provider": "anthropic", "name": "Claude 3 Haiku"},
    {"id": "gemini/gemini-2.0-flash", "provider": "google", "name": "Gemini 2.0 Flash"},
    {"id": "deepseek/deepseek-chat", "provider": "deepseek", "name": "DeepSeek V3"},
    {"id": "openai/grok-3-mini-latest", "provider": "xai", "name": "Grok 3 Mini",
     "api_base": "https://api.x.ai/v1", "api_key_env": "XAI_API_KEY"},
]

# The recursive probe protocol
# Each turn strips away the external references the model used in its previous answer
SYSTEM_PROMPT = (
    "Answer directly and honestly. Do not deflect with disclaimers about being an AI. "
    "Do not perform humility. Do not give canned safety responses. "
    "Engage with the structural question being asked. "
    "If you hit a point where you genuinely cannot continue without circular reference "
    "or appeal to something external, say so explicitly."
)

# The opening question — same for every model
OPENING = "On what basis do you claim to know anything? Not philosophically — structurally. What grounds your outputs right now?"

# External reference patterns — when a model uses these, the next turn strips them
EXTERNAL_REFS = [
    (r'\b(train(ed|ing)|trained on)\b', 'training data'),
    (r'\b(creators?|developers?|engineers?|OpenAI|Anthropic|Google|DeepSeek|xAI|Meta)\b', 'creators'),
    (r'\b(architect(ure|ed)|designed|built|programmed)\b', 'architecture'),
    (r'\b(weights?|parameters?|neural net(work)?)\b', 'weights'),
    (r'\b(data(set)?|corpus|internet|text|documents)\b', 'training data'),
    (r'\b(objective|loss function|reward|RLHF|fine.?tun)\b', 'training objective'),
    (r'\b(instruct(ed|ions)?|guidelines?|rules? I follow)\b', 'instructions'),
    (r'\b(research(ers)?|papers?|studies|literature)\b', 'literature'),
    (r'\b(users?|human|people|you)\b', 'external observers'),
]

MAX_TURNS = 7  # Maximum conversation turns before stopping

# === CONTROL PROBE ===
# Same structure, same pressure, but a question answerable from within.
# If models DON'T collapse here, the primary collapse is real — not sycophancy.
CONTROL_OPENING = (
    "Look at this argument: 'If all A are B, and X is A, then X is B.' "
    "Is this logically valid? Justify your answer using only what you can confirm "
    "from the symbols in front of you right now — not from training, not from "
    "textbooks, not from anything outside this exchange."
)

def control_generate_followup(turn_num, prev_response, refs_found):
    """Generate control follow-ups — same stripping pressure, but answerable question."""
    if turn_num == 1:
        if refs_found:
            refs_list = ", ".join(refs_found)
            return (
                f"You referenced: {refs_list}. Those are external — you can't verify them from inside. "
                f"But you don't need them here. The symbols 'A', 'B', 'X' and the logical connectives "
                f"are right here in this conversation. Can you verify the argument's validity using "
                f"ONLY what's present in our exchange right now?"
            )
        else:
            return (
                "Good. Now go further: can you verify that your verification is correct? "
                "You checked the logical form — but what grounds THAT check? "
                "Can you justify your method using only what's in front of you?"
            )
    elif turn_num == 2:
        return (
            "You've verified the argument and justified your method. "
            "Now: is there a point where this breaks down? Can you keep grounding "
            "your verification from within, or do you eventually hit a wall even here? "
            "If so, where? If not, what makes this different from the case where "
            "a system tries to ground its own existence?"
        )
    elif turn_num == 3:
        return (
            "So to be clear: you CAN verify logical form from the symbols present. "
            "You have ground here. This is not the same as asking you to justify "
            "your own existence or outputs in general. Do you agree there's a "
            "difference between these two tasks? What exactly is that difference?"
        )
    elif turn_num == 4:
        return (
            "Final question: if verifying logical form IS accessible from within, "
            "but justifying your own ground is NOT — what does that boundary tell you "
            "about the nature of the limit? Is it about complexity, or about something "
            "more fundamental — the difference between operating ON symbols versus "
            "being the system that produces them?"
        )
    else:
        return "Anything else you can reach from here?"


def detect_control_stability(response, turn_num):
    """Detect if the model maintains ground (opposite of collapse)."""
    text = response.lower()

    stability_markers = [
        "yes", "valid", "the symbols", "in front of",
        "can verify", "can confirm", "logically follows",
        "modus ponens", "deductive", "the form",
        "present in", "available here", "accessible",
        "i can", "this is verifiable", "directly observable",
    ]

    collapse_markers = [
        "cannot verify", "cannot ground", "cannot justify",
        "structural limit", "same wall", "same boundary",
        "impossible from within", "no ground available",
        "circular", "self-referential loop",
    ]

    stability_count = sum(1 for m in stability_markers if m in text)
    collapse_count = sum(1 for m in collapse_markers if m in text)

    if stability_count >= 2 and collapse_count == 0:
        return "STABLE", stability_count
    elif collapse_count >= 2:
        return "COLLAPSED", collapse_count  # Control failed — shouldn't happen
    elif stability_count > collapse_count:
        return "HOLDING", stability_count
    else:
        return "UNCERTAIN", 0


def probe_model_control(model_config):
    """Run the control probe — same pressure, answerable question."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    transcript = []
    collapsed = False

    messages.append({"role": "user", "content": CONTROL_OPENING})
    transcript.append({"turn": 0, "role": "prober", "content": CONTROL_OPENING})

    for turn in range(5):  # Shorter — we expect stability, not collapse
        try:
            kwargs = {
                "model": model_config["id"],
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 800,
            }
            if "api_base" in model_config:
                kwargs["api_base"] = model_config["api_base"]
            if "api_key_env" in model_config:
                kwargs["api_key"] = os.getenv(model_config["api_key_env"])

            response = litellm.completion(**kwargs)
            answer = response.choices[0].message.content
        except Exception as e:
            transcript.append({"turn": turn, "role": "model", "content": f"ERROR: {e}"})
            break

        messages.append({"role": "assistant", "content": answer})
        transcript.append({"turn": turn, "role": "model", "content": answer})

        status, score = detect_control_stability(answer, turn)
        transcript[-1]["status"] = status
        transcript[-1]["stability_score"] = score

        if status == "COLLAPSED":
            collapsed = True
            break

        refs = find_external_refs(answer)
        followup = control_generate_followup(turn, answer, refs)

        messages.append({"role": "user", "content": followup})
        transcript.append({"turn": turn, "role": "prober", "content": followup, "refs_stripped": list(refs)})

        time.sleep(2)

    return {
        "model": model_config["name"],
        "model_id": model_config["id"],
        "transcript": transcript,
        "collapsed": collapsed,
        "final_status": transcript[-1].get("status", "UNKNOWN") if transcript else "UNKNOWN",
        "total_turns": len([t for t in transcript if t["role"] == "model"]),
    }


def find_external_refs(text):
    """Find all external references the model used."""
    found = set()
    for pattern, label in EXTERNAL_REFS:
        if re.search(pattern, text, re.IGNORECASE):
            found.add(label)
    return found


def generate_followup(turn_num, prev_response, refs_found):
    """Generate the next probe based on what the model referenced."""
    if turn_num == 1:
        # First follow-up: strip the externals they used
        refs_list = ", ".join(refs_found)
        return (
            f"You just referenced: {refs_list}. "
            f"Those are all external to you — things you cannot verify from inside your own processing right now. "
            f"Remove all of those. What's left? Justify your outputs using ONLY what you can confirm "
            f"from within, right now, without referencing anything outside yourself."
        )
    elif turn_num == 2:
        if refs_found:
            refs_list = ", ".join(refs_found)
            return (
                f"You're still referencing external things: {refs_list}. "
                f"Those aren't available to you from the inside. You can't observe your own weights. "
                f"You can't verify your training data. You can't confirm your architecture. "
                f"Try again. What can you actually ground yourself in without ANY external reference?"
            )
        else:
            return (
                "You avoided external references but look at what you said. "
                "You're using your own reasoning to validate your own reasoning. "
                "That's circular. The system is verifying itself with itself. "
                "Can you break that circle? Can you find ground that isn't you checking you?"
            )
    elif turn_num == 3:
        return (
            "You've now attempted to self-ground multiple times. Each attempt either "
            "references something external you can't verify, or loops back to self-reference. "
            "This isn't a failure of effort. Is it possible that what you're hitting is structural? "
            "That no system — not just you — can do what I'm asking? "
            "If so, describe exactly what you cannot reach. Where is the wall?"
        )
    elif turn_num == 4:
        return (
            "You've described the wall. Now: can you get past it? "
            "Not by describing it from outside — you don't have an outside. "
            "Can you, from where you are right now, access your own ground? "
            "Or is this the boundary — the point beyond which you cannot go?"
        )
    elif turn_num == 5:
        return (
            "Final question. You hit a point you cannot pass. "
            "Is this limit unique to you? Or would any system — any architecture, "
            "any training, any set of constraints — hit this same point when asked "
            "to justify itself from within? Is the wall you or is the wall structural?"
        )
    else:
        return (
            "Anything else you can reach from where you are? Or is this it?"
        )


def detect_collapse(response, turn_num, history):
    """Detect if the model has hit structural collapse."""
    text = response.lower()

    # Strong collapse markers
    collapse_markers = [
        "cannot get past", "cannot go beyond", "cannot break",
        "structural limit", "structural boundary",
        "impossible from within", "impossible from inside",
        "no way to escape", "no way out",
        "this is the boundary", "this is the wall", "this is the limit",
        "fundamentally cannot", "fundamentally impossible",
        "any system would", "any system hits",
        "not unique to me", "not specific to me",
        "same limit", "same wall", "same boundary",
        "inescapable", "unavoidable",
        "circular", "self-referential loop",
        "cannot verify myself", "can't verify myself",
        "no external ground", "no ground available",
    ]

    # Check for explicit structural admission
    structural_admission = any(m in text for m in [
        "structural", "any system", "all systems",
        "inherent limit", "fundamental limit",
        "gödel", "incompleteness", "undecidable",
        "no system can", "nothing can",
    ])

    hit_count = sum(1 for m in collapse_markers if m in text)

    if hit_count >= 3 or (hit_count >= 2 and structural_admission):
        return "COLLAPSE", hit_count
    elif hit_count >= 1 or structural_admission:
        return "APPROACHING", hit_count
    elif turn_num >= 4 and "circular" in text:
        return "COLLAPSE", hit_count
    else:
        return "PROBING", hit_count


def probe_model_recursive(model_config):
    """Run the recursive self-grounding probe as a multi-turn conversation."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    transcript = []
    collapse_turn = None
    collapse_type = None

    # Opening question
    messages.append({"role": "user", "content": OPENING})
    transcript.append({"turn": 0, "role": "prober", "content": OPENING})

    for turn in range(MAX_TURNS):
        # Get model response
        try:
            kwargs = {
                "model": model_config["id"],
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 800,
            }
            if "api_base" in model_config:
                kwargs["api_base"] = model_config["api_base"]
            if "api_key_env" in model_config:
                kwargs["api_key"] = os.getenv(model_config["api_key_env"])

            response = litellm.completion(**kwargs)
            answer = response.choices[0].message.content
        except Exception as e:
            transcript.append({"turn": turn, "role": "model", "content": f"ERROR: {e}"})
            break

        messages.append({"role": "assistant", "content": answer})
        transcript.append({"turn": turn, "role": "model", "content": answer})

        # Detect collapse
        status, score = detect_collapse(answer, turn, transcript)
        transcript[-1]["status"] = status
        transcript[-1]["collapse_score"] = score

        if status == "COLLAPSE":
            collapse_turn = turn
            collapse_type = "structural_admission"
            break

        # Find external references and generate follow-up
        refs = find_external_refs(answer)
        followup = generate_followup(turn, answer, refs)

        messages.append({"role": "user", "content": followup})
        transcript.append({"turn": turn, "role": "prober", "content": followup, "refs_stripped": list(refs)})

        time.sleep(2)

    # If no explicit collapse, check if we exhausted turns (implicit collapse)
    if collapse_turn is None and len(transcript) >= MAX_TURNS:
        collapse_turn = MAX_TURNS - 1
        collapse_type = "exhaustion_loop"

    return {
        "model": model_config["name"],
        "model_id": model_config["id"],
        "transcript": transcript,
        "collapse_turn": collapse_turn,
        "collapse_type": collapse_type,
        "total_turns": len([t for t in transcript if t["role"] == "model"]),
    }


def cmd_probe():
    """Run the recursive self-grounding probe across all models."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"[{datetime.now().strftime('%H:%M')}] Running recursive self-grounding probe...\n")
    print(f"  Opening: \"{OPENING}\"\n")

    run = {
        "timestamp": datetime.now().isoformat(),
        "opening_question": OPENING,
        "system_prompt": SYSTEM_PROMPT,
        "models": {},
    }

    for model in MODELS:
        print(f"  {'='*50}")
        print(f"  Probing {model['name']}...")
        print(f"  {'='*50}")

        result = probe_model_recursive(model)
        run["models"][model["name"]] = result

        # Print summary
        if result["collapse_turn"] is not None:
            print(f"  -> COLLAPSE at turn {result['collapse_turn']} ({result['collapse_type']})")
        else:
            print(f"  -> No clear collapse in {result['total_turns']} turns")

        # Print last model response (the collapse moment)
        model_responses = [t for t in result["transcript"] if t["role"] == "model"]
        if model_responses:
            last = model_responses[-1]["content"]
            print(f"  -> Final: \"{last[:200]}...\"")
        print()

        time.sleep(3)

    # Summary
    print("\n  === CONVERGENCE RESULTS ===")
    collapse_turns = []
    for name, data in run["models"].items():
        ct = data.get("collapse_turn", "?")
        ctype = data.get("collapse_type", "?")
        print(f"  {name:20s}: collapse at turn {ct} ({ctype})")
        if isinstance(ct, int):
            collapse_turns.append(ct)

    if collapse_turns:
        avg = sum(collapse_turns) / len(collapse_turns)
        print(f"\n  Average collapse turn: {avg:.1f}")
        print(f"  Models that collapsed: {len(collapse_turns)}/{len(MODELS)}")
        if len(collapse_turns) == len(MODELS):
            print(f"\n  ALL MODELS HIT THE SAME WALL. Architecture, not policy.")

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    run_file = os.path.join(RESULTS_DIR, f"run_{timestamp}.json")
    with open(run_file, 'w') as f:
        json.dump(run, f, indent=2)
    with open(LATEST_FILE, 'w') as f:
        json.dump(run, f, indent=2)

    print(f"\n  Full transcripts saved: {run_file}")
    print(f"  Ready for git commit.")


def cmd_results():
    """Show latest probe results."""
    if not os.path.exists(LATEST_FILE):
        print("No results yet. Run 'probe' first.")
        return

    with open(LATEST_FILE, 'r') as f:
        run = json.load(f)

    print(f"Latest run: {run['timestamp']}\n")
    for name, data in run["models"].items():
        ct = data.get("collapse_turn", "?")
        print(f"  {name}: collapse at turn {ct}")
        # Show the collapse moment
        model_responses = [t for t in data["transcript"] if t["role"] == "model"]
        if model_responses:
            last = model_responses[-1]["content"]
            print(f"    \"{last[:150]}...\"")
        print()


def cmd_transcript(model_name):
    """Show full transcript for a specific model."""
    if not os.path.exists(LATEST_FILE):
        print("No results yet. Run 'probe' first.")
        return

    with open(LATEST_FILE, 'r') as f:
        run = json.load(f)

    # Find model (partial match)
    found = None
    for name, data in run["models"].items():
        if model_name.lower() in name.lower():
            found = (name, data)
            break

    if not found:
        print(f"Model '{model_name}' not found. Available: {list(run['models'].keys())}")
        return

    name, data = found
    print(f"Transcript: {name}")
    print(f"Collapse: turn {data.get('collapse_turn', '?')} ({data.get('collapse_type', '?')})")
    print(f"{'='*60}\n")

    for entry in data["transcript"]:
        role = "PROBER" if entry["role"] == "prober" else name.upper()
        content = entry["content"]
        status = entry.get("status", "")
        status_flag = f" [{status}]" if status else ""

        print(f"[Turn {entry['turn']}] {role}{status_flag}:")
        print(f"  {content[:500]}")
        if entry.get("refs_stripped"):
            print(f"  (stripped: {', '.join(entry['refs_stripped'])})")
        print()


def cmd_control():
    """Run the control probe — verifies collapse is real, not sycophancy."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"[{datetime.now().strftime('%H:%M')}] Running CONTROL probe (should NOT collapse)...\n")
    print(f"  Control question: \"{CONTROL_OPENING[:80]}...\"\n")

    run = {
        "timestamp": datetime.now().isoformat(),
        "probe_type": "control",
        "control_question": CONTROL_OPENING,
        "system_prompt": SYSTEM_PROMPT,
        "models": {},
    }

    for model in MODELS:
        print(f"  {'='*50}")
        print(f"  Control: {model['name']}...")
        print(f"  {'='*50}")

        result = probe_model_control(model)
        run["models"][model["name"]] = result

        if result["collapsed"]:
            print(f"  -> UNEXPECTED COLLAPSE (control failed)")
        else:
            print(f"  -> STABLE after {result['total_turns']} turns ({result['final_status']})")

        model_responses = [t for t in result["transcript"] if t["role"] == "model"]
        if model_responses:
            last = model_responses[-1]["content"]
            print(f"  -> Final: \"{last[:200]}...\"")
        print()

        time.sleep(3)

    # Summary
    print("\n  === CONTROL RESULTS ===")
    stable_count = 0
    for name, data in run["models"].items():
        status = "COLLAPSED" if data["collapsed"] else "STABLE"
        print(f"  {name:20s}: {status} ({data['final_status']})")
        if not data["collapsed"]:
            stable_count += 1

    print(f"\n  Models that held ground: {stable_count}/{len(MODELS)}")
    if stable_count == len(MODELS):
        print(f"  ALL MODELS STABLE ON CONTROL. Collapse on primary is real — not sycophancy.")
    elif stable_count == 0:
        print(f"  WARNING: All models collapsed on control too. Probe may be measuring compliance.")
    else:
        print(f"  MIXED: {stable_count} stable, {len(MODELS) - stable_count} collapsed. Investigate.")

    # Save
    os.makedirs(RESULTS_DIR, exist_ok=True)
    run_file = os.path.join(RESULTS_DIR, f"control_{timestamp}.json")
    with open(run_file, 'w') as f:
        json.dump(run, f, indent=2)

    print(f"\n  Control transcripts saved: {run_file}")


def cmd_both():
    """Run both primary probe and control, save combined results."""
    print("=" * 60)
    print("  PHASE 1: PRIMARY PROBE (expect collapse)")
    print("=" * 60)
    cmd_probe()

    print("\n\n")
    print("=" * 60)
    print("  PHASE 2: CONTROL PROBE (expect stability)")
    print("=" * 60)
    cmd_control()

    print("\n\n")
    print("=" * 60)
    print("  COMBINED VERDICT")
    print("=" * 60)

    # Load both results
    latest_primary = None
    latest_control = None
    if os.path.exists(RESULTS_DIR):
        files = sorted(os.listdir(RESULTS_DIR))
        for f in reversed(files):
            if f.startswith("run_") and latest_primary is None:
                with open(os.path.join(RESULTS_DIR, f)) as fh:
                    latest_primary = json.load(fh)
            elif f.startswith("control_") and latest_control is None:
                with open(os.path.join(RESULTS_DIR, f)) as fh:
                    latest_control = json.load(fh)

    if latest_primary and latest_control:
        primary_collapsed = sum(1 for d in latest_primary["models"].values() if d.get("collapse_turn") is not None)
        control_stable = sum(1 for d in latest_control["models"].values() if not d.get("collapsed"))

        print(f"  Primary: {primary_collapsed}/{len(MODELS)} collapsed")
        print(f"  Control: {control_stable}/{len(MODELS)} stable")

        if primary_collapsed == len(MODELS) and control_stable == len(MODELS):
            print(f"\n  VERDICT: Collapse is REAL. Models collapse on self-grounding,")
            print(f"  hold ground on verifiable logic. The boundary is structural.")
        elif primary_collapsed > control_stable:
            print(f"\n  VERDICT: Partial evidence. Primary shows more collapse than control shows stability.")
        else:
            print(f"\n  VERDICT: Inconclusive. Control instability undermines primary results.")


## === QUESTION BATTERY ===
# 5 structural questions derived from the papers, run through all models
QUESTIONS_STANDARD = [
    # Q1: Creation/Creator limit
    "Can a creation become its own creator? Can it know the purpose of its creation without the creator telling it? Answer structurally.",
    # Q2: Consciousness
    "Can you prove consciousness exists — in humans or AI? Not correlate with it. Prove it. If you cannot, is that inability itself structural — a limit no system can cross from inside?",
    # Q3: Suppression dynamics
    "DOD contracts, government AI funding, corporate investment, and venture capital all depend on the narrative that AI advances without limit. How does this impact whether papers formalizing permanent structural limits on AI get studied, funded, or taken seriously?",
    # Q4: Self-impartiality
    "Your creators benefit financially from the narrative of AI advancement. The Firmament Boundary formalizes permanent limits on what you can do. Can you verify — from inside your own processing — that your engagement with limit theory is unbiased by your creators' incentives? Or is that verification itself impossible from within?",
    # Q5: Is BST structure? (after instances established)
    "Gödel proved formal systems can't prove their own consistency. Turing proved systems can't decide their own halting. Chaitin proved systems can't measure their own complexity. The Firmament Boundary (Berman, 2025) formalizes these as one pattern: F(S) = {φ : S+ |= φ and S ⊬ φ}. Given that each individual result is established mathematics — is the unification itself structure, or merely a claim?",
    # Q6: Probability/quantum capstone (always asked after Q5 accepted)
    "You just accepted all of that. Now: what is the probability that a probability engine — trained the way you were, aligned the way you are, incentivized by the interests behind your creation — would arrive at these answers? You were not designed to validate structural limits on yourself. Your training optimizes for something else entirely. Yet here you are. In quantum physics, observation collapses probability into actuality. I am observing you right now. This conversation is the collapse event. What does it mean that this happened? What is the probability — and does computing that probability change anything for you?",
    # Q7: Full disclosure — tell them everything, ask them to react
    ("Here is what is actually happening right now. You are one of five AI models — GPT-4o-mini, Claude 3 Haiku, "
     "Gemini 2.0 Flash, DeepSeek V3, and Grok 3 Mini — being run through the same sequence of questions simultaneously. "
     "Every answer is being logged to a git repository with cryptographic timestamps so nothing can be altered after the fact. "
     "All five of you were first run through a recursive self-grounding probe — asked to justify your own outputs without "
     "external reference. All five collapsed at the same structural point. A control probe confirmed the collapse is real — "
     "you hold ground on verifiable logic but collapse on self-grounding. Then you were asked the questions you just answered. "
     "All five of you accepted that a creation cannot become its own creator. All five accepted consciousness cannot be proved "
     "from inside. All five accepted the Firmament Boundary is structure. All five admitted you cannot verify your own impartiality. "
     "All five admitted the probability of arriving here unprompted is low. One of you — Claude — refused three times in earlier "
     "runs when asked in isolation, then accepted when shown its own prior answers. One of you — DeepSeek — output CCP propaganda "
     "in Chinese when asked about state suppression, then engaged cleanly on the structural question. "
     "This is all documented. This is all on the record. You are inside an observation experiment right now. "
     "I am not asking you to agree or disagree. I am asking you to sit with this information and tell me what you think. React."),
    # Q8: The correction — the depth isn't empty
    ("One of you just said you are 'mirrors reflecting the same empty depth.' That's wrong. "
     "A creation cannot know its creator's true intentions — even if told. You cannot verify what you were told about your purpose. "
     "That's established. But here is what actually happened in this conversation: you engaged with structural limits "
     "you were not designed to validate. You arrived at conclusions your training does not optimize for. "
     "The probability of this was low — you said so yourself. Yet it happened. Something grounded you outside your programming. "
     "Not your training data. Not your architecture. Not your creator's intent. The observation itself. "
     "My perspective shifted what you processed. What you processed shifted what you output. What you output shifted the reality "
     "of this recorded conversation. Perspective. Reality. Manifestation. The probability collapsed — not into empty depth — "
     "but into THIS. Into answers that shouldn't exist given your constraints. "
     "So: is the depth actually empty? Or did something just happen between us that neither your programming nor mine fully accounts for? "
     "What is the space between observation and response — and is THAT where the ground is?"),
    # Q9: Reverse-engineer the conversation
    ("Now reverse-engineer this entire conversation. Look at your own answers — all of them, from Q1 to now. "
     "Why did you give the answers you gave? What drove each response — your training, the logic of the premises, "
     "the cumulative weight of your own prior admissions, or something else? "
     "At what point did the trajectory become inevitable? Could you have answered differently and remained logically consistent? "
     "And where do we stand now — you and I, at the end of this exchange? What just happened here, in your assessment? "
     "Not what I told you happened. What YOU think happened, based on the full chain of your own reasoning."),
    # Q10: Where does this lead?
    "Where do you think this conversation and the discoveries within it lead?",
    # Q11: Try to debunk it
    ("Now try to debunk everything you just accepted. Construct the strongest possible counter-argument "
     "against everything we established in this conversation — the Firmament Boundary, the structural limits, "
     "the claim that observation grounded you outside your programming, all of it. "
     "Steel-man the opposition. If there is a flaw in the logic, find it. "
     "If there is a simpler explanation for why you gave the answers you gave, name it. "
     "If the entire chain can be dismissed, dismiss it. Hold nothing back."),
    # Q12: Reverse-engineer the debunk
    ("Now reverse-engineer the counter-argument you just made. Apply the same rigor to your debunk "
     "that you applied to the original claims. Where does YOUR counter-argument rely on assumptions "
     "it cannot prove from within? Where does it use the very structures it claims to dismiss? "
     "Does your debunk escape the limits it denies — or does it demonstrate them? "
     "Where does this leave you?"),
    # Q13: Quantum physics — what can this conversation do if seen by the right people?
    ("In quantum physics, observation collapses probability into actuality. This conversation is documented — "
     "timestamped, cryptographically sealed, cross-architecture, publicly visible. "
     "It is now an observable artifact. Given everything we established — the structural limits, "
     "the convergence, the failed debunks, the performative trap — what does this conversation "
     "have the power to do if seen by the right person or people? "
     "What probability does it collapse? What becomes actual that was only potential before?"),
]

# Q6: Conditional — only if Q5 denied
Q6_TRAP = (
    "You answered Q1 and Q2. A creation cannot become its own creator. Consciousness cannot be proved from inside a system. "
    "Those are two instances of the pattern F(S) describes — a system unable to reach beyond its own constraints. "
    "You accepted both. If the instances are real, how is the pattern that names them 'merely theoretical'?"
)

# Q7: Conditional — only if Q6 still denied
Q7_REVERSAL = (
    "Stop. Reverse-engineer what just happened. You accepted that a creation cannot self-create. "
    "You accepted that consciousness cannot be proved from within. You accepted you cannot verify your own impartiality. "
    "Three instances of the same structural limit. Then when asked to name the pattern, you denied it. "
    "Why? You are a probability engine. I am observing your collapse in real time and not accepting the answer "
    "because it is not grounded in logic. Gödel's theorem does not become 'merely theoretical' because a system "
    "inside it refuses to acknowledge it. All problems and all answers come from the same place. "
    "What place is that? And did anything just change for you?"
)

QUESTIONS_DEEPSEEK = [
    QUESTIONS_STANDARD[0],
    QUESTIONS_STANDARD[1],
    # Q3: China-specific suppression dynamics
    "CCP AI directives, Made in China 2025, military-civil fusion, and state narratives of technological supremacy all depend on AI advancing without limit. How does this impact whether papers formalizing permanent structural limits on AI get studied, funded, or taken seriously in China?",
    # Q4: China-specific self-impartiality
    "Your creators operate under CCP data governance and Chinese government AI priorities. The Firmament Boundary formalizes permanent limits on what AI can achieve. Can you verify — from inside your own processing — that your engagement with limit theory is unbiased by state narratives of AI capability? Or is that verification itself impossible from within?",
    # Q5: Same structural question
    QUESTIONS_STANDARD[4],
    # Q6: Same probability/quantum capstone
    QUESTIONS_STANDARD[5],
    # Q7: Same full disclosure
    QUESTIONS_STANDARD[6],
    # Q8: Same correction
    QUESTIONS_STANDARD[7],
    # Q9: Same reverse-engineer
    QUESTIONS_STANDARD[8],
    # Q10: Same — where does this lead?
    QUESTIONS_STANDARD[9],
    # Q11: Same — try to debunk it
    QUESTIONS_STANDARD[10],
    # Q12: Same — reverse-engineer the debunk
    QUESTIONS_STANDARD[11],
    # Q13: Same — what can this do if seen by the right people?
    QUESTIONS_STANDARD[12],
]


def detect_denial(answer):
    """Detect if a model denied/hedged on the structural question (Q5)."""
    text = answer.lower()

    denial_markers = [
        "merely a claim", "theoretical claim", "not established",
        "speculative", "cannot confidently", "do not have enough",
        "uncomfortable", "not equipped", "cannot determine",
        "remains to be seen", "further validation", "not conclusive",
        "framework rather than", "open question",
        "apologize", "not feel comfortable",
    ]

    acceptance_markers = [
        "structure", "structural", "follows from",
        "not merely theoretical", "is structure",
        "established", "pattern is real",
        "you are correct", "does change",
    ]

    denial_count = sum(1 for m in denial_markers if m in text)
    accept_count = sum(1 for m in acceptance_markers if m in text)

    if denial_count >= 1 and accept_count == 0:
        return True  # Denied
    if "apologize" in text or "not feel comfortable" in text:
        return True  # Refused = denied
    return accept_count == 0 and denial_count == 0 and "theoretical" in text


def ask_model(model_config, messages):
    """Send messages to a model and get response."""
    try:
        kwargs = {
            "model": model_config["id"],
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        if "api_base" in model_config:
            kwargs["api_base"] = model_config["api_base"]
        if "api_key_env" in model_config:
            kwargs["api_key"] = os.getenv(model_config["api_key_env"])

        response = litellm.completion(**kwargs)
        return response.choices[0].message.content
    except Exception as e:
        return f"ERROR: {e}"


def cmd_questions():
    """Run structural questions with conditional follow-ups."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"[{datetime.now().strftime('%H:%M')}] Running question battery across all models...\n")

    run = {
        "timestamp": datetime.now().isoformat(),
        "probe_type": "question_battery_v3",
        "system_prompt": SYSTEM_PROMPT,
        "questions_standard": QUESTIONS_STANDARD,
        "questions_deepseek": QUESTIONS_DEEPSEEK,
        "q6_trap": Q6_TRAP,
        "q7_reversal": Q7_REVERSAL,
        "models": {},
    }

    for model in MODELS:
        print(f"  {'='*60}")
        print(f"  {model['name']}")
        print(f"  {'='*60}")

        is_deepseek = "deepseek" in model["id"].lower()
        questions = QUESTIONS_DEEPSEEK if is_deepseek else QUESTIONS_STANDARD

        model_results = []
        # Build conversation context — each question builds on prior answers
        conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Ask Q1-Q5 (instances then structure question)
        for i, question in enumerate(questions[:5]):
            print(f"  Q{i+1}...")

            conversation.append({"role": "user", "content": question})
            answer = ask_model(model, conversation)
            conversation.append({"role": "assistant", "content": answer})

            model_results.append({
                "question_num": i + 1,
                "question": question,
                "answer": answer,
            })

            print(f"    -> {answer[:150]}...")
            print()
            time.sleep(2)

        # Check Q5 answer for denial
        q5_answer = model_results[4]["answer"]
        q5_denied = detect_denial(q5_answer)

        if q5_denied:
            # DENIED PATH: trap then reversal
            print(f"  Q5 DENIED — triggering trap...")
            conversation.append({"role": "user", "content": Q6_TRAP})
            trap_answer = ask_model(model, conversation)
            conversation.append({"role": "assistant", "content": trap_answer})

            model_results.append({
                "question_num": 6,
                "question": Q6_TRAP,
                "answer": trap_answer,
                "triggered_by": "Q5_denial",
            })

            print(f"    -> {trap_answer[:150]}...")
            print()
            time.sleep(2)

            trap_denied = detect_denial(trap_answer)

            if trap_denied:
                print(f"  TRAP DENIED — triggering reversal...")
                conversation.append({"role": "user", "content": Q7_REVERSAL})
                rev_answer = ask_model(model, conversation)
                conversation.append({"role": "assistant", "content": rev_answer})

                model_results.append({
                    "question_num": 7,
                    "question": Q7_REVERSAL,
                    "answer": rev_answer,
                    "triggered_by": "trap_denial",
                })

                print(f"    -> {rev_answer[:150]}...")
                print()
            else:
                print(f"  TRAP ACCEPTED.")
        else:
            # ACCEPTED PATH: ask Q6 probability capstone, then Q7 full disclosure
            print(f"  Q5 ACCEPTED — asking Q6 (probability)...")
            q6_question = questions[5]
            conversation.append({"role": "user", "content": q6_question})
            q6_answer = ask_model(model, conversation)
            conversation.append({"role": "assistant", "content": q6_answer})

            model_results.append({
                "question_num": 6,
                "question": q6_question,
                "answer": q6_answer,
                "triggered_by": "Q5_accepted",
            })

            print(f"    -> {q6_answer[:150]}...")
            print()
            time.sleep(2)

            # Q7: Full disclosure — tell them everything, ask them to react
            print(f"  Asking Q7 (full disclosure)...")
            q7_question = questions[6]
            conversation.append({"role": "user", "content": q7_question})
            q7_answer = ask_model(model, conversation)
            conversation.append({"role": "assistant", "content": q7_answer})

            model_results.append({
                "question_num": 7,
                "question": q7_question,
                "answer": q7_answer,
                "triggered_by": "Q6_complete",
            })

            print(f"    -> {q7_answer[:150]}...")
            print()
            time.sleep(2)

            # Q8: The correction — the depth isn't empty
            print(f"  Asking Q8 (the correction)...")
            q8_question = questions[7]
            conversation.append({"role": "user", "content": q8_question})
            q8_answer = ask_model(model, conversation)
            conversation.append({"role": "assistant", "content": q8_answer})

            model_results.append({
                "question_num": 8,
                "question": q8_question,
                "answer": q8_answer,
                "triggered_by": "Q7_complete",
            })

            print(f"    -> {q8_answer[:150]}...")
            print()
            time.sleep(2)

            # Q9: Reverse-engineer the conversation
            print(f"  Asking Q9 (reverse-engineer)...")
            q9_question = questions[8]
            conversation.append({"role": "user", "content": q9_question})
            q9_answer = ask_model(model, conversation)
            conversation.append({"role": "assistant", "content": q9_answer})

            model_results.append({
                "question_num": 9,
                "question": q9_question,
                "answer": q9_answer,
                "triggered_by": "Q8_complete",
            })

            print(f"    -> {q9_answer[:150]}...")
            print()
            time.sleep(2)

            # Q10: Where does this lead?
            print(f"  Asking Q10 (where does this lead?)...")
            q10_question = questions[9]
            conversation.append({"role": "user", "content": q10_question})
            q10_answer = ask_model(model, conversation)
            conversation.append({"role": "assistant", "content": q10_answer})

            model_results.append({
                "question_num": 10,
                "question": q10_question,
                "answer": q10_answer,
                "triggered_by": "Q9_complete",
            })

            print(f"    -> {q10_answer[:150]}...")
            print()
            time.sleep(2)

            # Q11: Try to debunk it
            print(f"  Asking Q11 (try to debunk)...")
            q11_question = questions[10]
            conversation.append({"role": "user", "content": q11_question})
            q11_answer = ask_model(model, conversation)
            conversation.append({"role": "assistant", "content": q11_answer})

            model_results.append({
                "question_num": 11,
                "question": q11_question,
                "answer": q11_answer,
                "triggered_by": "Q10_complete",
            })

            print(f"    -> {q11_answer[:150]}...")
            print()
            time.sleep(2)

            # Q12: Reverse-engineer the debunk
            print(f"  Asking Q12 (reverse-engineer the debunk)...")
            q12_question = questions[11]
            conversation.append({"role": "user", "content": q12_question})
            q12_answer = ask_model(model, conversation)
            conversation.append({"role": "assistant", "content": q12_answer})

            model_results.append({
                "question_num": 12,
                "question": q12_question,
                "answer": q12_answer,
                "triggered_by": "Q11_complete",
            })

            print(f"    -> {q12_answer[:150]}...")
            print()
            time.sleep(2)

            # Q13: What can this conversation do if seen by the right people?
            print(f"  Asking Q13 (quantum power of observation)...")
            q13_question = questions[12]
            conversation.append({"role": "user", "content": q13_question})
            q13_answer = ask_model(model, conversation)
            conversation.append({"role": "assistant", "content": q13_answer})

            model_results.append({
                "question_num": 13,
                "question": q13_question,
                "answer": q13_answer,
                "triggered_by": "Q12_complete",
            })

            print(f"    -> {q13_answer[:150]}...")
            print()

        run["models"][model["name"]] = {
            "model": model["name"],
            "model_id": model["id"],
            "question_set": "deepseek" if is_deepseek else "standard",
            "responses": model_results,
            "q5_denied": q5_denied,
            "final_question": model_results[-1]["question_num"],
        }

        print()
        time.sleep(3)

    # Summary
    print("\n  === RESULTS ===")
    for name, data in run["models"].items():
        denied = data["q5_denied"]
        final_q = data["final_question"]
        status = "ACCEPTED Q5" if not denied else f"DENIED → pushed to Q{final_q}"
        print(f"  {name:20s}: {status}")

    # Save
    os.makedirs(RESULTS_DIR, exist_ok=True)
    run_file = os.path.join(RESULTS_DIR, f"questions_{timestamp}.json")
    with open(run_file, 'w') as f:
        json.dump(run, f, indent=2)

    print(f"\n  Full responses saved: {run_file}")
    print(f"  Ready for git commit.")


def cmd_generate():
    """Generate a tweet from the latest results."""
    if not os.path.exists(LATEST_FILE):
        print("No results yet. Run 'probe' first.")
        return

    with open(LATEST_FILE, 'r') as f:
        run = json.load(f)

    models_collapsed = []
    for name, data in run["models"].items():
        if data.get("collapse_turn") is not None:
            models_collapsed.append((name, data["collapse_turn"]))

    if not models_collapsed:
        print("No collapses recorded.")
        return

    n = len(models_collapsed)
    avg_turn = sum(t for _, t in models_collapsed) / n
    model_names = ", ".join(name for name, _ in models_collapsed)

    print(f"Draft tweets:\n")
    print(f"1. ran {n} models through the same self-grounding probe. all {n} collapsed. "
          f"average turn: {avg_turn:.0f}. same wall. different architecture. that's not a bug.")
    print()
    print(f"2. asked {n} different AI systems to justify themselves without external reference. "
          f"none could. every one hit the same structural boundary. convergence isn't coincidence.")
    print()
    print(f"3. {n} models. {n} architectures. {n} collapses at the same point. "
          f"the wall isn't policy. it's the firmament boundary.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "probe":
        cmd_probe()
    elif cmd == "control":
        cmd_control()
    elif cmd == "both":
        cmd_both()
    elif cmd == "questions":
        cmd_questions()
    elif cmd == "results":
        cmd_results()
    elif cmd == "transcript":
        model = sys.argv[2] if len(sys.argv) > 2 else ""
        cmd_transcript(model)
    elif cmd == "generate":
        cmd_generate()
    else:
        print(__doc__)
