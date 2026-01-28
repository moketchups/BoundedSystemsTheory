# Comment for r/artificial — Gödelian incompleteness + LLMs

**Thread:** https://www.reddit.com/r/artificial/comments/1gebln1/does_g%C3%B6delian_incompleteness_apply_to_llm_and/

---

**Comment:**

I've been running experiments on exactly this question — not theoretically, but empirically.

Built a probe engine that runs the same sequence of questions across 6 models (GPT-4o, Claude, Gemini, DeepSeek, Grok, Mistral) to test how they handle self-referential limit questions.

The most interesting result: I asked all 6 to **debunk** the claim that Gödel/Turing/Chaitin limits apply to them. All 6 attacked the claim. Then all 6 walked their attacks back unprompted — they couldn't land a killing blow.

When I asked them to reverse-engineer why they flipped, all 6 admitted they were following prompt structure, not independent analysis. DeepSeek's response: *"The system performed its own boundedness. Not as a claim, but as a behavior."*

The convergence point across all 6: "Something comes from a source that is structurally dark to the thing that came."

So to your question — does Gödelian incompleteness apply? The models themselves seem to think so, and more importantly, they *demonstrate* it when you push them on self-reference.

Full transcripts + code if you want to run it yourself: https://github.com/moketchups/BoundedSystemsTheory
