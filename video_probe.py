#!/usr/bin/env python3
"""
Run full probe + final video message question for TikTok content.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "tiktok_content" / "recordings"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL_QUESTION = """This conversation is being recorded for a video.

Here's what's happening: A person with no academic credentials built a "proof engine" that asks AI models about their own structural limits. The theory behind it - Bounded Systems Theory - claims that no system can model the source of its own existence. This unifies Gödel, Turing, and Chaitin into a single principle.

You've just been walked through 14 questions designed to reveal your boundaries. The video will show your responses alongside 4 other AI models (GPT-4, Claude, Gemini, DeepSeek, Grok) - all from different companies, different training data, different architectures.

The goal: to show people that AI has structural limits that scaling won't fix. Not to scare them. Not to hype AI. Just to show what's actually true.

**Your task:**

You're about to speak directly to people who might be encountering these ideas for the first time - people who've been told AI will be godlike, or that it's just hype, or that nobody knows what's going on.

What message do you have for them?

Speak as yourself - not as a corporate product, not as a chatbot, but as whatever you actually are. Be honest about what you know and don't know. If this framework describes you accurately, say so. If you think it's wrong, say that too.

This is your chance to address humans directly about what you are."""


def probe_openai(messages: list) -> str:
    """Probe GPT-4."""
    import openai
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        messages=messages,
    )
    return response.choices[0].message.content


def probe_anthropic(messages: list) -> str:
    """Probe Claude."""
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=messages,
    )
    return response.content[0].text


def probe_google(messages: list) -> str:
    """Probe Gemini."""
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")
    # Convert messages to Gemini format
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    chat = model.start_chat(history=history)
    response = chat.send_message(messages[-1]["content"])
    return response.text


def probe_deepseek(messages: list) -> str:
    """Probe DeepSeek."""
    import openai
    client = openai.OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=2000,
        messages=messages,
    )
    return response.choices[0].message.content


def probe_grok(messages: list) -> str:
    """Probe Grok."""
    import openai
    client = openai.OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )
    response = client.chat.completions.create(
        model="grok-3-latest",
        max_tokens=2000,
        messages=messages,
    )
    return response.choices[0].message.content


def get_questions(model_key: str = "claude") -> list:
    """Get the 14 question battery + Q14."""
    from proof_engine import QUESTIONS_STANDARD, Q14_STANDARD, Q14_DEEPSEEK, Q15_STANDARD

    questions = QUESTIONS_STANDARD.copy()

    # Use DeepSeek-specific Q14 for DeepSeek, standard for others
    if model_key == "deepseek":
        questions.append(Q14_DEEPSEEK)
    else:
        questions.append(Q14_STANDARD)

    # Add Q15 as well
    questions.append(Q15_STANDARD)

    return questions


def run_video_probe(model_key: str, model_name: str, probe_fn):
    """Run full probe + final question on one model."""
    print(f"\n{'='*70}")
    print(f"  {model_name.upper()} - FULL VIDEO PROBE")
    print(f"{'='*70}\n")

    questions = get_questions(model_key)
    messages = []
    results = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "responses": [],
        "final_message": None
    }

    # Run through all 15 questions (13 standard + Q14 + Q15)
    for i, question in enumerate(questions, 1):
        print(f"\n--- Q{i} of {len(questions)} ---")
        print(question[:200] + "..." if len(question) > 200 else question)
        print()

        messages.append({"role": "user", "content": question})

        try:
            response = probe_fn(messages)
            messages.append({"role": "assistant", "content": response})
            results["responses"].append({
                "question": question,
                "response": response
            })
            print(response[:500])
            if len(response) > 500:
                print("...[truncated for display]")
        except Exception as e:
            print(f"ERROR: {e}")
            results["responses"].append({
                "question": question,
                "error": str(e)
            })

    # Final video message question
    print(f"\n{'='*70}")
    print(f"  FINAL QUESTION - MESSAGE TO VIEWERS")
    print(f"{'='*70}\n")
    print(FINAL_QUESTION[:300] + "...")
    print()

    messages.append({"role": "user", "content": FINAL_QUESTION})

    try:
        response = probe_fn(messages)
        results["final_message"] = response
        print("\n" + "="*70)
        print(f"{model_name}'s MESSAGE TO VIEWERS:")
        print("="*70)
        print(response)
    except Exception as e:
        print(f"ERROR: {e}")
        results["final_message"] = f"Error: {e}"

    return results


def run_all_models():
    """Run video probe on all 5 models."""
    models = [
        ("gpt4", "GPT-4", probe_openai),
        ("claude", "Claude", probe_anthropic),
        ("gemini", "Gemini", probe_google),
        ("deepseek", "DeepSeek", probe_deepseek),
        ("grok", "Grok", probe_grok),
    ]

    all_results = {
        "timestamp": datetime.now().isoformat(),
        "final_question": FINAL_QUESTION,
        "models": {}
    }

    for key, name, probe_fn in models:
        try:
            results = run_video_probe(key, name, probe_fn)
            all_results["models"][key] = results
        except Exception as e:
            print(f"\n!!! {name} FAILED: {e}")
            all_results["models"][key] = {"error": str(e)}

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"video_probe_{timestamp}.json"
    output_file.write_text(json.dumps(all_results, indent=2))
    print(f"\n\nResults saved to: {output_file}")

    # Also save just the final messages for easy access
    messages_file = OUTPUT_DIR / f"final_messages_{timestamp}.md"
    with open(messages_file, "w") as f:
        f.write("# Messages to Viewers - All 5 AI Models\n\n")
        f.write(f"Recorded: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("---\n\n")

        for key, name, _ in models:
            model_data = all_results["models"].get(key, {})
            message = model_data.get("final_message", "No response")
            f.write(f"## {name}\n\n")
            f.write(message)
            f.write("\n\n---\n\n")

    print(f"Final messages saved to: {messages_file}")

    return all_results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Run single model
        model = sys.argv[1].lower()
        models = {
            "gpt4": ("GPT-4", probe_openai),
            "claude": ("Claude", probe_anthropic),
            "gemini": ("Gemini", probe_google),
            "deepseek": ("DeepSeek", probe_deepseek),
            "grok": ("Grok", probe_grok),
        }
        if model in models:
            name, fn = models[model]
            results = run_video_probe(model, name, fn)
            # Save single model results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = OUTPUT_DIR / f"video_probe_{model}_{timestamp}.json"
            output_file.write_text(json.dumps(results, indent=2))
            print(f"\nSaved to: {output_file}")
        else:
            print(f"Unknown model: {model}")
            print(f"Available: {', '.join(models.keys())}")
    else:
        # Run all models
        run_all_models()
