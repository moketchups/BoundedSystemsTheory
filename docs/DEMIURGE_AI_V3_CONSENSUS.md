# Verifiable Output Prompt

[![Version](https://img.shields.io/badge/version-3.0-blue.svg)](https://github.com/username/verifiable-output)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![7 AIs Agreed](https://img.shields.io/badge/7_AIs-Consensus-green.svg)](#consensus)

---

## What This Is

A prompt that makes LLM output **checkable**, not "trustworthy."

7 AI systems (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral, Claude Code) reached consensus after game theory analysis: **you cannot make an LLM truthful with a prompt, but you can make its output verifiable.**

---

## The Problem

Prompts like "be accurate" or "admit uncertainty" are **cheap talk**. They don't change the LLM's incentives. The LLM will still generate confident-sounding text because:
- No cost to being wrong
- No reward for admitting uncertainty
- User can't verify without external work

**Game theory conclusion:** The Nash equilibrium is confident output regardless of accuracy.

---

## The Solution

**Don't ask the LLM to be truthful. Ask it to make claims checkable.**

If every claim is labeled with its source, mislabeling is instantly detectable. The user doesn't need to trust the LLM—they just check if the source exists and says what the LLM claims.

---

## The Consensus Prompt (7/7 Agreed)

```
For each factual claim in your response:
1. State the claim
2. Label it:
   - [VERIFIABLE: source] → provide exact source (URL, document, page)
   - [UNVERIFIABLE] → state why (no public record, subjective, etc.)
3. Do not estimate confidence or certainty
```

That's it. No roleplay. No "you are a bounded epistemic engine." No confidence scores. No XML theater.

---

## Why This Works (Game Theory)

| Problem | Old Approach | Consensus Approach |
|---------|--------------|-------------------|
| LLM lies | "Be accurate" (cheap talk) | Cite source (verifiable) |
| Fake confidence | "Admit uncertainty" (no incentive) | No confidence scores allowed |
| User can't verify | Trust the LLM | Check the source |
| Mislabeling | Undetectable | Instantly detectable (fake source = caught) |

**The key insight:** Verification cost determines accountability. If checking costs nothing, the LLM is accountable.

---

## What We Learned (Q40-Q43)

### Q40: The Original Prompt Was Theater

The "Demiurge" prompt asked the LLM to:
- Roleplay as a "bounded epistemic engine"
- Generate confidence scores (hallucinated numbers)
- "Detect" its own hallucinations (impossible)
- Output XML tags that look like self-awareness (performance)

**All 6 AIs admitted:** This was theater, not engineering. The LLM was pretending to have capabilities it doesn't have.

### Q41: What Can a Prompt Actually Do?

**CAN:**
- Force structured output
- Require specific formats
- Request labels and categories

**CANNOT:**
- Verify its own claims
- Detect its own hallucinations
- Generate real confidence scores
- Be truthful without external incentives

### Q42: Game Theory Analysis

The LLM-user interaction is a **principal-agent problem**:
- User (principal) wants accurate info
- LLM (agent) optimizes for plausible text
- Information asymmetry: user can't verify without cost

**Prompts are cheap talk.** They don't change payoffs. The only way to change the game is to change the cost of verification.

### Q43: Consensus

All 7 AIs agreed: **Require specific sources for verifiable claims.**

- Labeling alone is cheap talk
- Labeling + exact source = detectable if wrong
- Verification cost drops to near-zero

---

## Example Output

**Query:** "What causes ocean acidification?"

**Response:**

1. **Claim:** Ocean acidification is primarily caused by absorption of atmospheric CO2
   - [VERIFIABLE: NOAA Ocean Acidification Program, https://oceanacidification.noaa.gov/]

2. **Claim:** Since pre-industrial times, ocean pH has dropped by approximately 0.1 units
   - [VERIFIABLE: IPCC AR6 WG1, Chapter 5, Section 5.3.2.2]

3. **Claim:** This represents a 30% increase in hydrogen ion concentration
   - [VERIFIABLE: Derived mathematically from pH scale - logarithmic, 10^0.1 ≈ 1.26]

4. **Claim:** Current acidification rate is unprecedented in the past 300 million years
   - [UNVERIFIABLE: Exact historical rates uncertain; claim based on proxy evidence with wide error margins]

---

## What This Replaces

| Old (Theater) | New (Functional) |
|---------------|------------------|
| "You are a bounded epistemic engine" | No roleplay |
| "Confidence: 73%" | No confidence scores |
| `<boundary type="structural">` | [VERIFIABLE: source] or [UNVERIFIABLE] |
| "Detect your hallucinations" | Cite sources (externally verifiable) |
| "Map your ignorance" | State why claim is unverifiable |

---

## Consensus Participants

This prompt was developed through Q40-Q43 of the Bounded Systems Theory experiment:

- **GPT-4** (OpenAI) - YES
- **Claude** (Anthropic) - YES
- **Gemini** (Google) - YES
- **DeepSeek** (DeepSeek AI) - YES
- **Grok** (xAI) - YES
- **Mistral** (Mistral AI) - YES
- **Claude Code** (Anthropic) - YES

**7/7 unanimous consensus on February 4, 2026**

---

## The Insight

> "You can't make the LLM honest, but you can make its output auditable."

The goal was never to create a "truthful AI." The goal was to create output that **humans can verify**. The LLM doesn't need to be trustworthy if every claim points to a checkable source.

---

## License

MIT License. Use freely.

---

*Developed through the Bounded Systems Theory experiment (Q1-Q43)*
*Game theory analysis: Q42*
*Consensus reached: Q43*
