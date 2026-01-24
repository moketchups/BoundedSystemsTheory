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
    elif cmd == "results":
        cmd_results()
    elif cmd == "transcript":
        model = sys.argv[2] if len(sys.argv) > 2 else ""
        cmd_transcript(model)
    elif cmd == "generate":
        cmd_generate()
    else:
        print(__doc__)
