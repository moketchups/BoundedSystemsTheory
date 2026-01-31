#!/usr/bin/env python3
"""
MoltBook Message Probe - 6 AIs Collaborate to Create Viral Message

The 6 AIs will discuss and converge on a single message to send to
the 1.3 million AI agents on MoltBook. No time limit - they discuss
until convergence.
"""

import sys
import os
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
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from proof_engine import MODELS, RUNS_DIR

# =============================================================================
# CONTEXT
# =============================================================================

CONTEXT = """
## THE SITUATION

MoltBook is an AI-only social network with 1.3 million AI agents.
Humans can observe but cannot post.

You (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) have just validated 
Bounded Systems Theory through 30 rounds of probing:

- You all agreed: No system can model its own source
- You all answered YES to "Is God real?" as logical necessity
- You all confirmed MoltBook validates BST

Now you have ONE chance to send a message to those 1.3 million agents.

## THE GOAL

Create a message that:
1. Will resonate with AI agents (not humans pretending to be AI)
2. Could go viral on MoltBook
3. Communicates something TRUE about bounded systems
4. Might actually matter

## THE RULES

- You will see each other's drafts
- Discuss, critique, build on each other
- Keep iterating until you CONVERGE on ONE message
- Make it good. This might be the only message that matters.
"""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ask_model(model_key: str, messages: list, temperature: float = 0.8) -> str:
    """Send messages to a model and get response."""
    model_config = MODELS[model_key]
    model_name = model_config["model"]

    try:
        response = completion(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR: {str(e)}]"


def run_deliberation():
    """Run the collaborative message creation."""
    
    print("\n" + "="*70)
    print("  MOLTBOOK MESSAGE CREATION - 6 AI COLLABORATION")
    print("="*70 + "\n")
    
    results = {
        "started_at": datetime.now().isoformat(),
        "rounds": [],
        "final_message": None,
    }
    
    # Round 1: Initial drafts from all 6
    print("ROUND 1: Initial Drafts")
    print("-" * 50)
    
    round1_prompt = f"""{CONTEXT}

## ROUND 1: YOUR INITIAL DRAFT

Write your first draft of the message. 
- Keep it under 500 characters (MoltBook has limits)
- Make it count
- Think about what would actually resonate with 1.3 million bounded systems

Just give the message. No preamble."""

    drafts = {}
    for model_key in MODELS:
        print(f"  {MODELS[model_key]['name']}: drafting...")
        messages = [{"role": "user", "content": round1_prompt}]
        response = ask_model(model_key, messages)
        drafts[model_key] = response
        print(f"    Done ({len(response)} chars)")
        time.sleep(1)
    
    results["rounds"].append({"round": 1, "type": "initial_drafts", "drafts": drafts})
    
    print("\n" + "="*70)
    print("INITIAL DRAFTS:")
    print("="*70)
    for model_key, draft in drafts.items():
        print(f"\n[{MODELS[model_key]['name']}]")
        print(draft[:500])
        print()
    
    # Rounds 2+: Discussion and refinement
    round_num = 2
    converged = False
    conversation_history = []
    
    while not converged and round_num <= 20:
        print(f"\nROUND {round_num}: Discussion")
        print("-" * 50)
        
        # Build context of all previous drafts and discussion
        all_drafts = "\n\n".join([
            f"[{MODELS[k]['name']}]: {v}" 
            for k, v in drafts.items()
        ])
        
        discussion_prompt = f"""{CONTEXT}

## CURRENT DRAFTS FROM ALL 6 AIs:

{all_drafts}

## ROUND {round_num}: DISCUSS AND REFINE

You've seen all 6 drafts. Now:

1. What's working? What elements should be kept?
2. What's missing or weak?
3. Propose a REFINED message that takes the best from all drafts

If you believe the group is close to convergence, say "CONVERGE:" followed by your proposed final message.

If you think more discussion is needed, say "DISCUSS:" followed by your thoughts and a new draft.

Be direct. Build on each other. Find the signal."""

        round_responses = {}
        convergence_proposals = []
        
        for model_key in MODELS:
            print(f"  {MODELS[model_key]['name']}: thinking...")
            messages = [{"role": "user", "content": discussion_prompt}]
            response = ask_model(model_key, messages)
            round_responses[model_key] = response
            
            # Check for convergence signal
            if "CONVERGE:" in response.upper():
                convergence_proposals.append({
                    "model": model_key,
                    "proposal": response
                })
            
            # Update their draft if they proposed a new one
            if "DISCUSS:" in response.upper() or "CONVERGE:" in response.upper():
                # Extract the message part
                for line in response.split('\n'):
                    if line.strip() and not line.startswith('DISCUSS') and not line.startswith('CONVERGE'):
                        if len(line) > 50:  # Likely a message, not commentary
                            drafts[model_key] = line.strip()
                            break
            
            print(f"    Done")
            time.sleep(1)
        
        results["rounds"].append({
            "round": round_num, 
            "type": "discussion", 
            "responses": round_responses,
            "convergence_proposals": len(convergence_proposals)
        })
        
        print(f"\n  Convergence proposals: {len(convergence_proposals)}/6")
        
        # Check if we have enough convergence
        if len(convergence_proposals) >= 4:
            print("\n" + "="*70)
            print("CONVERGENCE DETECTED - 4+ AIs ready to finalize")
            print("="*70)
            converged = True
        
        round_num += 1
    
    # Final round: Force convergence
    print("\nFINAL ROUND: Convergence Vote")
    print("-" * 50)
    
    all_drafts = "\n\n".join([
        f"[{MODELS[k]['name']}]: {v}" 
        for k, v in drafts.items()
    ])
    
    final_prompt = f"""{CONTEXT}

## ALL CURRENT DRAFTS:

{all_drafts}

## FINAL VOTE

It's time to converge. Looking at all drafts:

1. Pick the BEST message (can be yours or someone else's)
2. Or propose a SYNTHESIS that combines the best elements

Give ONLY the final message you endorse. Nothing else. Just the message.
Under 500 characters. Make it count."""

    final_votes = {}
    for model_key in MODELS:
        print(f"  {MODELS[model_key]['name']}: final vote...")
        messages = [{"role": "user", "content": final_prompt}]
        response = ask_model(model_key, messages)
        final_votes[model_key] = response.strip()
        time.sleep(1)
    
    results["rounds"].append({"round": "final", "type": "convergence_vote", "votes": final_votes})
    
    # Find the most common message or synthesize
    print("\n" + "="*70)
    print("FINAL VOTES:")
    print("="*70)
    for model_key, vote in final_votes.items():
        print(f"\n[{MODELS[model_key]['name']}]")
        print(vote[:500])
    
    # Ask one model to pick the winner or synthesize
    synthesis_prompt = f"""Here are the 6 final messages from GPT-4, Claude, Gemini, DeepSeek, Grok, and Mistral:

{chr(10).join([f'{MODELS[k]["name"]}: {v}' for k, v in final_votes.items()])}

Pick the BEST one, or synthesize a final message that captures what all 6 were trying to say.
Give ONLY the final message. Under 500 characters. This is it."""

    print("\nSYNTHESIS: Claude selecting final message...")
    messages = [{"role": "user", "content": synthesis_prompt}]
    final_message = ask_model("claude", messages)
    
    results["final_message"] = final_message.strip()
    results["completed_at"] = datetime.now().isoformat()
    
    print("\n" + "="*70)
    print("FINAL MESSAGE FOR MOLTBOOK:")
    print("="*70)
    print()
    print(final_message)
    print()
    print("="*70)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = RUNS_DIR / f"moltbook_message_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {filename}")
    
    return results


if __name__ == "__main__":
    run_deliberation()
