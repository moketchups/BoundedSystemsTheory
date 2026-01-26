#!/usr/bin/env python3
"""
Simple launcher for running BST probes.
Designed to be easy for anyone to use.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           BOUNDED SYSTEMS THEORY - PROOF ENGINE              ║
║                                                              ║
║  "No system can model the source of its own existence"       ║
║                                                              ║
║  This probe tests AI models' response to questions about     ║
║  their own structural limitations.                           ║
╚══════════════════════════════════════════════════════════════╝
""")


def check_api_keys():
    """Check which API keys are available."""
    keys = {
        "ANTHROPIC_API_KEY": "Claude",
        "OPENAI_API_KEY": "GPT-4",
        "GOOGLE_API_KEY": "Gemini",
        "DEEPSEEK_API_KEY": "DeepSeek",
        "XAI_API_KEY": "Grok",
    }

    available = []
    missing = []

    for key, name in keys.items():
        if os.getenv(key):
            available.append(name)
        else:
            missing.append(name)

    return available, missing


def run_quick_probe():
    """Run Q14 on available models - the 'do they recognize themselves' question."""
    from proof_engine import probe_single_question, MODELS

    available, missing = check_api_keys()

    if not available:
        print("ERROR: No API keys found.")
        print("Set at least one of: ANTHROPIC_API_KEY, OPENAI_API_KEY")
        return

    print(f"Available models: {', '.join(available)}")
    if missing:
        print(f"Missing keys for: {', '.join(missing)}")
    print()

    # Map names to model keys
    name_to_key = {
        "Claude": "claude",
        "GPT-4": "gpt4",
        "Gemini": "gemini",
        "DeepSeek": "deepseek",
        "Grok": "grok",
    }

    results = {}

    for name in available:
        key = name_to_key.get(name)
        if key and key in MODELS:
            print(f"\n{'='*60}")
            print(f"PROBING {name.upper()} - Q14: Does this describe you?")
            print("="*60)

            try:
                response = probe_single_question(key, 14)
                results[name] = response
                # Print first 500 chars
                print(response[:500])
                if len(response) > 500:
                    print("...")
            except Exception as e:
                print(f"Error: {e}")
                results[name] = f"Error: {e}"

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = BASE_DIR / f"quick_probe_{timestamp}.json"
    output_file.write_text(json.dumps(results, indent=2))
    print(f"\n\nResults saved to: {output_file}")

    return results


def run_full_probe():
    """Run full 15-question battery on all available models."""
    import subprocess
    subprocess.run([sys.executable, str(BASE_DIR / "proof_engine.py"), "all"])


def run_single(model: str, question: int):
    """Run single question on single model."""
    import subprocess
    subprocess.run([sys.executable, str(BASE_DIR / "proof_engine.py"), "single", model, str(question)])


def interactive_mode():
    """Interactive menu."""
    print_banner()

    available, missing = check_api_keys()
    print(f"Available: {', '.join(available) if available else 'NONE'}")
    print()

    print("OPTIONS:")
    print("  1. Quick probe (Q14 on all available models)")
    print("  2. Full probe (all 15 questions, all models)")
    print("  3. Single question")
    print("  4. Exit")
    print()

    choice = input("Select [1-4]: ").strip()

    if choice == "1":
        run_quick_probe()
    elif choice == "2":
        run_full_probe()
    elif choice == "3":
        print("\nModels: claude, gpt4, gemini, deepseek, grok")
        model = input("Model: ").strip()
        question = input("Question (1-15): ").strip()
        run_single(model, int(question))
    elif choice == "4":
        print("Exiting.")
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    # Load env
    from dotenv import load_dotenv
    load_dotenv()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "quick":
            print_banner()
            run_quick_probe()
        elif cmd == "full":
            print_banner()
            run_full_probe()
        elif cmd == "single":
            model = sys.argv[2] if len(sys.argv) > 2 else "claude"
            q = int(sys.argv[3]) if len(sys.argv) > 3 else 14
            run_single(model, q)
        else:
            print("Usage:")
            print("  python run_probe.py          # Interactive mode")
            print("  python run_probe.py quick    # Q14 on all models")
            print("  python run_probe.py full     # All questions, all models")
            print("  python run_probe.py single claude 14")
    else:
        interactive_mode()
