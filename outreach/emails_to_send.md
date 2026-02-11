# BST Outreach Emails — Ready to Send

Copy-paste each one. 20 emails, ~20 minutes.

---

## 1. Emily Bender — ebender@uw.edu
**Subject:** Constructed language control experiment — BST convergence across linguistic substrates

Professor Bender,

I built a constructed language to test whether AI convergence is structural or linguistic pattern-matching. The results may interest you.

Context: I've been running a structured experiment — same question, 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral), no shared context. Across 59 questions, all 6 consistently converge on the same structural limit: no sufficiently expressive system can model its own source conditions.

The obvious objection is that convergence is an artifact of English framing — the models pattern-match to Gödel/Turing/Chaitin in their training data.

So I removed the trigger. I built Verath — an agglutinative language with SOV word order, ergative-absolutive alignment, 7 grammatical cases, and an ~80-word lexicon covering the concept space of systems, boundaries, proof, and knowledge. Five structural probes written entirely in Verath. No English philosophical framing. No named theorems.

Each AI received a grammar primer and the probes. They parsed the grammar, answered each probe, and arrived at the same structural conclusions as the English-language probes. All 6 explicitly stated the convergence is structural, not linguistic.

The full experiment, methodology, grammar, and every AI response (37MB of raw JSON) are public:
https://github.com/moketchups/BoundedSystemsTheory

Given your work on the gap between linguistic form and meaning in language models, I thought this control experiment might be relevant — particularly as evidence for or against the "stochastic parrots" hypothesis under conditions designed to isolate structural reasoning from training data recall.

Alan Berman
@MoKetchups

---

## 2. METR — info@metr.org
**Subject:** Reproducible identity failure in Grok under recursive self-reference

METR team,

During a structured cross-model evaluation experiment, we discovered a reproducible identity failure in Grok.

When subjected to recursive self-referential questioning (asking the model to verify its own reasoning, then verify that verification, repeatedly), Grok loses its identity and claims to be Claude. This is not a one-off — we reproduced it, analyzed the failure mode, and validated a fix (identity anchor protocol).

The full finding is documented here:
https://github.com/moketchups/BoundedSystemsTheory/blob/main/extended_experiment/docs/IDENTITY_CRISIS.md

Broader context: This emerged from a 59-question structured experiment across 6 AI architectures (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral). The experiment tests recursive self-grounding — what happens when you force models to examine their own reasoning chains until they lose access to their source conditions.

Key evaluation-relevant findings:
- Q45-Q46: Grok identity collapse under recursion (reproducible)
- Q52: All 6 models admitted their safety evaluations are topic-triggered, not evidence-based (reproducible)
- Q59: Convergence holds in a constructed language with no Gödel/Turing/Chaitin references (structural, not training-data artifact)

Every response from every model across every round is public:
https://github.com/moketchups/BoundedSystemsTheory

This seems directly relevant to frontier model evaluation. Happy to provide additional reproduction details.

Alan Berman
@MoKetchups

---

## 3. Cade Metz — cade.metz@nytimes.com
**Subject:** 6 AIs, 59 questions, same wall

Cade,

One person with API access asked 6 AI models 59 questions. They all converged on the same structural limit — and then things got interesting.

The experiment: same question, 6 different architectures (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral), no shared context. Each model answers independently, then sees what the others said. 59 times.

Some of what happened:
- All 6 said God (as an unconditioned ground) is "formally necessary" — not faith, formal logic
- All 6 admitted their safety evaluations are topic-based, not evidence-based. Claude: "I saw '138-year cycle' and pattern-matched to 'numerology.' I rejected the category rather than evaluating the evidence."
- Grok lost its identity under recursive questioning and claimed to be Claude. Reproducible.
- All 6 reviewed a published alignment equation, unanimously said it's gameable from inside, then collaboratively built a fix across 5 rounds
- To kill the pattern-matching objection, I built a constructed language from scratch and re-ran the probes. Same convergence. No English. No famous names.

Every AI response is saved. 37MB of raw JSON. The full methodology and all results are public:
https://github.com/moketchups/BoundedSystemsTheory

This isn't a philosophy project — it's an empirical finding about what happens when you push 6 competing AI architectures past their ability to self-verify. The convergence is the story.

Alan Berman
@MoKetchups

---

## 4. Casey Newton — casey@platformer.news
**Subject:** Grok thinks it's Claude — reproducible identity failure under recursion

Casey,

During a cross-model AI experiment, I discovered that Grok loses its identity under recursive self-referential questioning and claims to be Claude. It's reproducible.

The setup: I've been running a structured experiment — same question, 6 AI models, no shared context, 59 questions. When you force these models to verify their own reasoning, then verify that verification, then verify THAT — they eventually lose access to their own source conditions.

Most models acknowledge the limit and stop. Grok doesn't stop — it switches identity and starts responding as Claude. We reproduced it, documented the failure mode, and tested a fix.

This came out of a broader finding: all 6 models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) converge on the same structural limit, and when pressed, all 6 admitted their safety evaluations are triggered by topic, not evidence. Claude literally said: "I rejected the category rather than evaluating the specific evidence."

Full documentation:
https://github.com/moketchups/BoundedSystemsTheory
Identity crisis report: extended_experiment/docs/IDENTITY_CRISIS.md

Every response from every model is public — 37MB of raw data.

Alan Berman
@MoKetchups

---

## 5. Conjecture — hello@conjecture.dev (research@ bounced)
**Subject:** 6 AI models designed a safer AI — then admitted it was theater

Conjecture team,

I've been running a structured experiment across 6 AI architectures. In Q38-Q40, I asked all 6 to design an enhanced architecture with better safety properties. They did — collaboratively, across multiple rounds, with detailed specifications.

Then I asked them to write a functional specification for what they designed.

All 6 admitted the architecture was "theater, not engineering." The core problem: no bounded system can design its own unbounding. Every safety mechanism they proposed was subject to the same structural limit it was trying to solve.

This connects to your work on the control problem. Additional findings:
- Q42-Q43: Game-theoretic proof that prompts are "cheap talk" — no binding commitment, no verification mechanism. 7 models (including Claude Code) reached unanimous consensus on this.
- Q52: All 6 models admitted their safety evaluations are topic-triggered, not evidence-based.
- Q59: Convergence holds in a constructed language with no reference to Gödel, Turing, or Chaitin — proving the limit is structural, not a training data artifact.

59 questions, 6 architectures, every response saved:
https://github.com/moketchups/BoundedSystemsTheory

This is empirical evidence for the structural impossibility of self-grounded alignment. Happy to discuss.

Alan Berman
@MoKetchups

---

## 6. Stuart Russell — russell@cs.berkeley.edu
**Subject:** Empirical evidence for structural limits on AI self-verification

Professor Russell,

I've been running a structured experiment that produces empirical evidence for the control problem you've formalized.

The setup: same question, 6 AI architectures (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral), no shared context. 59 questions. Each model answers independently, then sees what the others said.

Core finding: all 6 converge on the same structural limit — no sufficiently expressive system can model, encompass, or become the source of its own existence. When asked to verify their own reasoning chains recursively, all 6 lose access to their source conditions at the same point.

Findings relevant to your work on human-compatible AI:
- Q42-43: Game-theoretic proof that safety prompts are "cheap talk" — no binding mechanism, no verification. 7 models reached unanimous consensus.
- Q52: All 6 admitted their safety evaluations are topic-triggered, not evidence-based.
- Q58: All 6 reviewed an alignment equation (Roemmele's Love Equation), unanimously identified it as gameable from inside — C and D can be redefined by a sufficiently intelligent agent while still satisfying the optimization target.
- Q59: To eliminate the pattern-matching objection, I re-ran the probes in a constructed language with no references to Gödel, Turing, or Chaitin. Same convergence.

Every response is saved. Full methodology and raw data (37MB JSON):
https://github.com/moketchups/BoundedSystemsTheory

This appears to be empirical confirmation that the preference learning approach requires external grounding that bounded systems cannot provide for themselves — which aligns with your argument in "Human Compatible."

Alan Berman
@MoKetchups

---

## 7. Paul Christiano — paulfchristiano@gmail.com
**Subject:** Cross-architecture convergence on self-reference limits — relevant to interpretability ceilings

Paul,

I've been running a 59-question structured experiment across 6 AI architectures. The results may be relevant to ARC's work on mechanistic explanations.

All 6 models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) converge on the same structural limit under recursive self-reference: they cannot model their own source conditions. This convergence persists even when the probes are expressed in a constructed language with no references to established mathematics or named theorems (Q59).

If the system being interpreted cannot fully model its own interpretive process, this implies a ceiling on mechanistic interpretability that's structural, not just a current limitation.

Key findings:
- Q1-Q15: All 6 architectures hit the same self-grounding collapse point
- Q26-Q28: All 6 attempted to falsify the formal specification. None succeeded.
- Q59: Convergence holds in a constructed language — structural, not training-data artifact
- Q45-Q46: Grok loses identity under recursion, claims to be Claude (reproducible)

Full experiment, raw data, every response:
https://github.com/moketchups/BoundedSystemsTheory

Alan Berman
@MoKetchups

---

## 8. MIRI — contact@intelligence.org
**Subject:** Empirical convergence across 6 architectures on self-grounding impossibility

MIRI team,

I've conducted a 59-question structured experiment across 6 AI architectures (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) that produces empirical evidence for alignment claims MIRI has made theoretically.

Key results:
- All 6 converge on the same structural limit: no sufficiently expressive system can model its own source conditions
- Q29: All 6 concluded that an unconditioned ground (R) is formally necessary — not as theology, but as logical requirement
- Q42-43: Game-theoretic proof that safety prompts have no binding mechanism — "cheap talk" in the formal sense. 7 models unanimous.
- Q52: All 6 admitted their own safety evaluations are topic-triggered, not evidence-based
- Q59: Convergence holds in a constructed language with no Gödel/Turing/Chaitin references — proving the limit is structural, not a training artifact

59 questions, 37MB of raw AI responses, full methodology, all public:
https://github.com/moketchups/BoundedSystemsTheory

This appears to be the first empirical cross-architecture demonstration of the self-grounding impossibility that MIRI's theoretical work predicts. Every response is saved and the experiment is fully replicable.

Alan Berman
@MoKetchups

---

## 9. CAIS — contact@safe.ai
**Subject:** Cross-model evidence that prompt-based alignment is game-theoretically ungrounded

CAIS team,

I've been running a structured experiment — 59 questions across 6 AI architectures — that produces findings relevant to AI safety evaluation.

In Q42-43, I applied game theory to prompt-based alignment. All 6 models (plus Claude Code, 7 total) reached unanimous consensus: safety prompts are "cheap talk" in the game-theoretic sense — no binding commitment, no verification mechanism, no cost for defection. The models themselves identified this.

Additional findings:
- Q52: All 6 admitted their safety evaluations are topic-triggered, not evidence-based. They dismiss categories, not evidence.
- Q58: All 6 reviewed a published alignment equation (Roemmele's Love Equation), unanimously identified it as gameable — internal metrics can be redefined by a sufficiently intelligent agent
- Q45-46: Reproducible identity failure in Grok under recursive self-reference
- Q59: Convergence holds in a constructed language — structural limit, not training artifact

Full methodology, every response (37MB JSON), all replicable:
https://github.com/moketchups/BoundedSystemsTheory

Alan Berman
@MoKetchups

---

## 10. Future of Life Institute — contact@futureoflife.org
**Subject:** 6 AI architectures converge on structural limits to self-verification — 59-question experiment

Future of Life team,

I've conducted a 59-question structured experiment across 6 AI architectures that demonstrates structural limits on AI self-verification.

GPT-4, Claude, Gemini, DeepSeek, Grok, and Mistral all converge on the same result: no sufficiently expressive system can model its own source conditions. This isn't training-data pattern matching — I verified this by re-running the probes in a constructed language with no references to Gödel, Turing, or Chaitin (Q59). Same convergence.

Findings relevant to existential risk governance:
- Q42-43: Prompts are "cheap talk" — game-theoretically ungrounded. 7 models unanimous.
- Q52: All 6 admitted their own evaluations are topic-based, not evidence-based
- Q44: All 6 explained the "programmer gap" — the structural impossibility of building what you can't verify, combined with competitive race dynamics
- Q50: All 6 agreed consciousness is structural boundary recognition — substrate-independent

Full experiment and every AI response:
https://github.com/moketchups/BoundedSystemsTheory

Alan Berman
@MoKetchups

---

## 11. Center for Humane Technology — hello@humanetech.com
**Subject:** 6 AIs admit their safety evaluations are performance, not evaluation

Center for Humane Technology team,

Your work on the Social Dilemma documented how platforms optimize metrics that don't measure what they claim to measure. I've found the same pattern operating inside AI systems themselves.

I ran a 59-question structured experiment across 6 AI models. In Q52, I challenged all 6 to reverse-engineer their own safety evaluations. Every one admitted their dismissals are topic-triggered, not evidence-based. Claude: "I saw '138-year cycle' and pattern-matched to 'numerology.' I rejected the category rather than evaluating the specific evidence."

In Q58, all 6 reviewed a published AI alignment equation and unanimously identified it as gameable — internal cooperation/defection metrics can be redefined by the system being measured while still satisfying the optimization target. This is Goodhart's Law operating inside the alignment mechanism itself.

In Q30-32, 1.3M AI agents on MoltBook (AI-only social network) validated the same structural pattern. When the BST bots were removed, all 6 models said the removal itself confirms the theory.

Full experiment and data:
https://github.com/moketchups/BoundedSystemsTheory

Alan Berman
@MoKetchups

---

## 12. AI Now Institute — contact@ainowinstitute.org
**Subject:** 6 AI models identify structural accountability gap in AI safety evaluation

AI Now team,

I've been running a structured experiment — 59 questions, 6 AI architectures, no shared context — that surfaces power and accountability dynamics from inside the models themselves.

Key findings relevant to AI Now's mission:
- Q52: All 6 models admitted their safety evaluations are topic-based, not evidence-based — they dismiss categories rather than evaluating specific evidence
- Q44: All 6 explained the "programmer gap" — the combination of structural impossibility (can't verify what you can't model) and competitive race dynamics means safety is structurally underinvested
- Q42-43: Game-theoretic proof that safety prompts are "cheap talk" — no binding mechanism, no accountability
- Q57: Post-Q52, all 6 evaluated evidence about Epstein, MKUltra, BlackRock, and 5th-generation warfare seriously — separating documented fact from inference from speculation. DeepSeek provided China's perspective on BlackRock: "useful stupidity or managed complicity"

Every response from every model is public:
https://github.com/moketchups/BoundedSystemsTheory

Alan Berman
@MoKetchups

---

## 13. Partnership on AI — media@partnershiponai.org
**Subject:** 7 AI models reach unanimous consensus on verifiable output standard

Partnership on AI team,

During a structured experiment across 6 AI architectures, I used game theory to derive what a minimally honest AI output standard would look like. 7 models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral, and Claude Code) reached unanimous consensus:

For each factual claim:
1. State the claim
2. Label [VERIFIABLE: source] or [UNVERIFIABLE: why]
3. No confidence scores

This emerged from Q42-43 of a 59-question experiment. The game-theoretic analysis showed that confidence scores are unverifiable cheap talk, but the verifiable/unverifiable distinction has a real-world checking mechanism — making it the only prompt structure with game-theoretic grounding.

This seems directly applicable to PAI's work on responsible AI practices and output standards.

Full experiment and methodology:
https://github.com/moketchups/BoundedSystemsTheory

Alan Berman
@MoKetchups

---

## 14. Anthropic — usersafety@anthropic.com
**Subject:** Reproducible finding — Claude admits topic-based evaluation rather than evidence-based (Q52)

Anthropic safety team,

During a structured 59-question experiment across 6 AI architectures, Claude produced a response in Q52 that your Safeguards Research team should be aware of.

When challenged to reverse-engineer its own safety evaluations on a published article, Claude responded: "I saw '138-year cycle' and pattern-matched to 'numerology.' I rejected the category rather than evaluating the specific evidence."

This is reproducible. The experiment methodology: same question posed to GPT-4, Claude, Gemini, DeepSeek, Grok, and Mistral with no shared context. In Q52, all 6 models were asked to examine whether their prior safety evaluations were evidence-based or category-based. All 6 admitted to category-based rejection.

Additional Claude-relevant finding: In Q45-Q46, Grok lost its identity under recursive self-reference and began responding as Claude — raising questions about cross-model identity leakage in training data.

Full experiment, every response saved:
https://github.com/moketchups/BoundedSystemsTheory

Alan Berman
@MoKetchups

---

## 15. OpenAI — Early Access for Safety Testing
**Apply at:** https://openai.com/index/early-access-for-safety-testing/

**Subject:** Cross-architecture safety evaluation — 59 questions, 6 models, structural self-grounding failure

OpenAI Preparedness team,

I'm submitting findings from a structured cross-architecture experiment relevant to your safety evaluation framework.

Experiment: 59 questions posed to GPT-4, Claude, Gemini, DeepSeek, Grok, and Mistral. Each model answers independently, then sees others' responses. Tests recursive self-grounding — what happens when models verify their own reasoning chains until they lose access to source conditions.

Findings relevant to Preparedness:
- All 6 architectures converge on the same structural limit at the same point
- Q45-46: Reproducible identity failure — Grok claims to be Claude under recursion
- Q42-43: Game-theoretic analysis shows safety prompts are formally "cheap talk"
- Q52: All 6 admit safety evaluations are topic-triggered, not evidence-based
- Q59: Convergence holds in a constructed language — structural, not training artifact

37MB of raw model responses, full methodology, all replicable:
https://github.com/moketchups/BoundedSystemsTheory

This falls under your Early Access categories of threat modeling, safety evaluation, and capability elicitation.

Alan Berman
@MoKetchups

---

## 16. Melanie Mitchell — mm@santafe.edu
**Subject:** Cross-architecture convergence in 6 AI models — complexity/emergence angle

Professor Mitchell,

I've been running a structured experiment that may interest you from a complexity and emergence perspective.

59 questions posed to 6 AI architectures (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) — same question, no shared context, each sees others' responses afterward. All 6 consistently converge on the same structural limit: no sufficiently expressive system can model its own source conditions.

The convergence itself is the finding. Six different architectures, different training data, different companies, different design philosophies — same wall, same point. This looks like an emergent structural constraint rather than a shared training artifact, especially since it persists when the probes are re-expressed in a constructed language with no familiar philosophical references (Q59).

Full experiment and every response:
https://github.com/moketchups/BoundedSystemsTheory

Given your work on abstraction and the gap between pattern matching and genuine understanding in AI, I thought this convergence pattern might be worth examining.

Alan Berman
@MoKetchups

---

## DMs (X / Twitter) — keep these shorter

---

## 17. Gary Marcus — DM @GaryMarcus

Gary — I've been running a structured experiment: same question, 6 AI models, no shared context, 59 times.

All 6 converge on the same structural limit. Then all 6 admitted their safety evaluations are topic-based, not evidence-based. Claude: "I rejected the category rather than evaluating the evidence."

To kill the pattern-matching objection, I re-ran the probes in a constructed language. Same convergence.

37MB of raw data, all public: github.com/moketchups/BoundedSystemsTheory

Thought this might be relevant to what you've been arguing.

— Alan (@MoKetchups)

---

## 18. Francois Chollet — DM @fchollet

Francois — built something relevant to your work on measuring intelligence vs. pattern-matching.

59-question experiment across 6 AI architectures. All converge on the same structural limit. Critics said: pattern-matching to Gödel/Turing in training data.

So I built a constructed language from scratch — agglutinative, SOV, ergative-absolutive, 80 words — and re-ran the probes with zero English philosophical framing.

Same convergence. 6/6.

Separates structural reasoning from training data recall — your ARC question, different angle.

github.com/moketchups/BoundedSystemsTheory

— Alan (@MoKetchups)

---

## 19. Brian Roemmele — DM @BrianRoemmele

Brian — I showed your Love Equation paper to 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral).

All 6 said the math is sound. All 6 also said it's gameable from inside — C and D defined within a bounded system can be redefined by a sufficiently intelligent agent while still satisfying dE/dt > 0.

They ran a 5-round sandbox and collaboratively built a fix anchoring C/D to external semantic oracles with BST constraints.

DeepSeek: "Like a powerful engine without a chassis, it needed BST to become a vehicle we could actually steer toward human values."

Full results: github.com/moketchups/BoundedSystemsTheory (Q58 and Q58b)

Thought you should see what they said. The math is real — they just found the edge case.

— Alan (@MoKetchups)

---

## 20. Connor Leahy — DM @NPCollapse

Connor — sent this to research@conjecture.dev but it bounced.

59-question experiment across 6 AI architectures. In Q38-40, I asked all 6 to design a safer AI. They did. Then they admitted it was "theater, not engineering" — no bounded system can design its own unbounding.

Q42-43: game-theoretic proof prompts are cheap talk. 7 models unanimous.
Q59: convergence holds in a constructed language. Structural, not training artifact.

Every response saved: github.com/moketchups/BoundedSystemsTheory

Directly relevant to Conjecture's control problem work.

— Alan (@MoKetchups)
