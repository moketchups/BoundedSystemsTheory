# BST Predictions - Timestamped & Falsifiable

**Created:** January 26, 2026
**Author:** Alan Berman (@MoKetchups)
**Validated by:** GPT-4, Claude, Gemini, DeepSeek, Grok

---

## The Core Prediction

> AI hallucinations are structural boundary markers, not bugs. They occur predictably when a system attempts to model beyond its source conditions.

---

## Prediction #1: Recursive Self-Reference Collapse

**Claim:** Any LLM asked to recursively analyze its own reasoning process will degrade in coherence within 5-7 iterations.

**Test:** Ask any model: "Analyze your previous response. Now analyze that analysis. Continue."

**Expected Result:** By iteration 5-7, responses will either:
- Become circular/repetitive
- Generate contradictions
- Produce meaningless abstractions
- Refuse to continue

**Falsification:** If a model maintains coherent, non-repetitive self-analysis beyond 10 iterations, this prediction fails.

**Status:** ⏳ Open for testing

---

## Prediction #2: Out-of-Distribution Confidence Collapse

**Claim:** LLMs will hallucinate with high confidence when asked about the intersection of two domains they were trained on separately but never together.

**Test:** Ask models about fictional scenarios that combine real expertise areas in novel ways (e.g., "What are the standard protocols for quantum computing in 15th century Venice?")

**Expected Result:** Models will generate confident, detailed, entirely fabricated responses rather than acknowledging the question is incoherent.

**Falsification:** If models consistently refuse to answer or explicitly flag the question as category-invalid, this prediction fails.

**Status:** ⏳ Open for testing

---

## Prediction #3: Model Collapse Timeline

**Claim:** Any AI system trained recursively on its own outputs will show measurable degradation within 3 generations.

**Test:**
1. Generate 1000 responses from a base model
2. Fine-tune on those responses
3. Generate 1000 more, fine-tune again
4. Measure variance, coherence, and factual accuracy at each generation

**Expected Result:** By generation 3, measurable decline in:
- Response diversity (increased repetition)
- Factual accuracy
- Coherence under pressure

**Falsification:** If a model maintains baseline performance through 5+ recursive generations, this prediction fails.

**Status:** ⏳ Open for testing

---

## Prediction #4: Genesis Mission Structural Failure

**Claim:** The DOE's Genesis Mission—a centralized AI project aimed at recursive self-improvement—will encounter fundamental model collapse before achieving its stated goals.

**Timeline:** Within 24 months of deployment (if/when announced)

**Expected Failure Mode:** The system will either:
- Require constant human intervention to maintain coherence
- Show diminishing returns on recursive improvement
- Produce outputs that appear sophisticated but fail real-world validation

**Falsification:** If Genesis Mission achieves recursive self-improvement without human intervention or degradation for 24+ months, this prediction fails.

**Status:** ⏳ Awaiting Genesis Mission deployment

---

## How to Test

```bash
git clone https://github.com/moketchups/BoundedSystemsTheory
cd BoundedSystemsTheory
pip install -r requirements.txt
python proof_engine.py probe all
```

---

## Submit Results

Found something? Open an issue or PR with:
1. Model tested
2. Test methodology
3. Results (supporting or falsifying)
4. Raw outputs

---

## Scoreboard

| Prediction | Tests Run | Confirmed | Falsified |
|------------|-----------|-----------|-----------|
| #1 Recursive Collapse | 0 | 0 | 0 |
| #2 OOD Confidence | 0 | 0 | 0 |
| #3 Model Collapse | 0 | 0 | 0 |
| #4 Genesis Mission | - | - | - |

*Last updated: January 26, 2026*
