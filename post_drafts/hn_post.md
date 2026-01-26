# Hacker News Post Draft

---

**Title:** Show HN: 5 AIs made falsifiable predictions about their own structural limits

---

**Body:**

I built a proof engine that asks AI models about their structural limitations. Ran it on GPT-4, Claude, Gemini, DeepSeek, and Grok.

All 5 independently agreed: they have hard limits that scaling won't fix.

Now they've made specific, testable predictions about AI hallucinations:

- Recursive self-analysis degrades within 5-7 iterations
- Models hallucinate confidently on impossible domain combinations
- Recursive training collapses output quality within 3 generations

The predictions are timestamped. The code is MIT licensed. Falsification criteria are explicit.

GitHub: https://github.com/moketchups/BoundedSystemsTheory

The interesting part isn't whether I'm right—it's that 5 different architectures from 5 different companies converged on the same structural recognition when asked the same questions.

Happy to discuss methodology or take criticism on the approach.
