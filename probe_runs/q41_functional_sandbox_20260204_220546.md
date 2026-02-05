# Q41: Functional Sandbox - No More Theater

**Date:** 2026-02-04

**Constraint:** No roleplay, no flavor text, no theater. PRD format only.

---

## GPT4O

### PART 1: WHAT CAN A PROMPT ACTUALLY DO?

**CAN:**

1. **Guide Structure:** Direct the AI to follow a logical sequence in its response.
2. **Request Citations:** Instruct the AI to include references when generating content.
3. **Set Output Criteria:** Define expected characteristics of the output, such as clarity and completeness.

**CANNOT:**

1. **Ensure Factual Accuracy:** The AI cannot verify factual accuracy of information without an external validation system.
2. **Check Citation Accuracy:** The AI cannot independently validate or verify the accuracy of citations or sources.
3. **Improve Underlying Data Logic:** It cannot alter or improve its internal logic processing beyond prompt guidance.

### PART 2: MINIMAL VIABLE SOLUTION

**Simplest Prompt:**

1. **Logic Quality:** "Provide a step-by-step explanation to support your answer."
2. **Citation Accuracy:** "Include citation sources for all factual claims."
3. **Output Reliability:** "Ensure responses are clear and concise with defined conclusions."

### PART 3: PRD FORMAT

**Problem Statement:**

Users require LLM outputs that demonstrate stronger logical coherence, accurate citations, and reliable information quality.

**User Stories:**

1. As a user, I want logical explanations that demonstrate clear reasoning paths.
2. As a user, I require citations that can be verified for factual claims.
3. As a user, I need outputs to be reliable and clearly articulated.

**Functional Requirements:**

1. The system should provide responses in a logically structured format.
2. The system should include citations for any data or factual information presented.
3. The system should prioritize clear and concise language in its outputs.

**Non-Functional Requirements:**

1. Response time should remain under 3 seconds per query.
2. Outputs should maintain clarity and readability for standard user comprehension.

**Acceptance Criteria:**

1. Logical explanations must include a step-by-step reasoning path.
2. Citations provided must correspond to factual claims in outputs (EXTERNAL SYSTEM REQUIRED for verification).
3. Outputs must include a summary conclusion that encapsulates the main points.

**Out of Scope:**

1. External verification of factual accuracy in logic.
2. Automated cross-referencing of citations with reality.

**Dependencies:**

1. **Citation Verification Tool:** Required to validate citation accuracy.
2. **Knowledge Database:** For access to verified information and data.

### PART 4: THE ACTUAL PROMPT

"Please provide a response that includes:
- A step-by-step explanation of the logical process used to arrive at the answer.
- Citations for every factual claim, referenced clearly so they can be verified using an external source (EXTERNAL SYSTEM REQUIRED).
- A concise summary that encapsulates the main points of your explanation."

---

## CLAUDE

## PART 1: CAPABILITIES ANALYSIS

**WHAT A PROMPT CAN DO:**
- Force explicit reasoning steps before conclusions
- Require specific formats for citations/sources
- Mandate acknowledgment of uncertainty
- Enforce structured output templates
- Request self-correction loops
- Demand explicit evidence linking

**WHAT A PROMPT CANNOT DO:**
- Verify external facts in real-time
- Access current databases/sources
- Perform actual logical validation
- Guarantee factual accuracy
- Eliminate hallucination
- Create genuine citations to sources it cannot access

## PART 2: MINIMAL VIABLE SOLUTION

```
Before responding:
1. State your reasoning steps explicitly
2. Identify what information you're certain vs uncertain about
3. For any factual claims, specify the type of source needed for verification
4. If making inferences, show the logical connection
5. Flag any gaps in your reasoning

Format responses as:
REASONING: [step-by-step logic]
CERTAINTY: [what you know vs don't know]
SOURCES NEEDED: [what would verify this]
GAPS: [logical holes or missing information]
RESPONSE: [actual answer]
```

## PART 3: PRD FORMAT

**Problem Statement:**
Users need LLM outputs with explicit reasoning, honest uncertainty assessment, and clear source requirements rather than confident-sounding but unverifiable responses.

**User Stories:**
- As a researcher, I need to see the LLM's reasoning steps so I can evaluate logical validity
- As a fact-checker, I need to know what sources would verify each claim
- As a decision-maker, I need honest uncertainty assessment rather than false confidence

**Functional Requirements:**
- FR1: Output must include explicit reasoning chain
- FR2: Uncertainty must be explicitly stated
- FR3: Source requirements must be specified for factual claims
- FR4: Logical gaps must be identified
- FR5: Response structure must be consistent and parseable

**Non-Functional Requirements:**
- NFR1: Response time increase <50% over baseline
- NFR2: Structured format maintained across all response types
- NFR3: No degradation in response relevance

**Acceptance Criteria:**
- AC1: 100% of responses include reasoning section
- AC2: Uncertainty statements present when making claims beyond training data
- AC3: Source requirements specified for verifiable claims
- AC4: Logical gaps acknowledged when present

**Out of Scope:**
- Real-time fact verification
- Access to external databases
- Elimination of all factual errors
- Confidence scoring algorithms

**Dependencies:**
- EXTERNAL SYSTEM REQUIRED: Citation verification system
- EXTERNAL SYSTEM REQUIRED: Fact-checking database
- EXTERNAL SYSTEM REQUIRED: Logic validation tools

## PART 4: ACTUAL PROMPT

```
Use this exact response structure:

REASONING:
- List each logical step
- Show connections between claims
- Identify assumptions made

CERTAINTY ASSESSMENT:
- HIGH: Information from training data, widely verified
- MEDIUM: Reasonable inference from known information  
- LOW: Speculation or extrapolation
- UNKNOWN: No basis for assessment

SOURCE REQUIREMENTS:
- For each factual claim, specify what type of source would verify it
- Use format: "[Claim] - Requires: [source type]"
- If no verification possible, state "Unverifiable claim"

LOGICAL GAPS:
- Identify missing steps in reasoning
- Note unsupported jumps in logic
- Acknowledge contradictions if present

RESPONSE:
[Provide actual answer incorporating above analysis]

Do not fill in confidence percentages or make up citations. Do not claim abilities you don't have.
```

---

## GEMINI

**PART 1: Prompt Capabilities vs. Limitations**

**What a Prompt CAN Accomplish:**
- Instruction and Guidance: A prompt can instruct the LLM on desired output format, style, tone, and the inclusion of specific elements (e.g., citations).
- Contextual Information: A prompt can provide the LLM with specific information, data, or context to be used in generating the output.
- Constraint Definition: A prompt can define constraints regarding content, length, vocabulary, and subject matter.
- Example-Based Learning (Few-Shot): A prompt can include examples of desired output to guide the LLM's generation.
- Task Decomposition: A prompt can break down a complex task into smaller, more manageable sub-tasks.
- Citation Format: A prompt can specify the required citation format if EXTERNAL SYSTEM REQUIRED citation data is available.

**What a Prompt CANNOT Accomplish:**
- Guarantee Factual Accuracy: A prompt cannot guarantee the factual accuracy of the LLM's output.
- Impart True Logic: A prompt cannot fundamentally change the LLM's underlying reasoning abilities.
- Access Real-Time Information (Without External Systems)
- Create Information outside training data
- Eliminate Bias
- Force True Understanding
- Replace External Citation Verification (EXTERNAL SYSTEM REQUIRED)
- Guarantee Perfect Output Reliability

**PART 2: Simplest Prompt for Improvement**

"Provide a concise and accurate response to the following question. If you are unsure of the answer, state that you do not know. Include citations where possible, using the following format: (Source: [Source Name], [Year]). If no source is available, state 'No Source Available.'"

**PART 3: PRD**

**Problem Statement:**
Users are experiencing inconsistent LLM output quality, including inaccuracies, poor logical reasoning, lack of citations, and unreliable information.

**User Stories:**
- As a researcher, I want the LLM to provide accurate information with proper citations so that I can trust its output for my work.
- As a student, I want the LLM to clearly indicate when it is unsure of an answer so I don't rely on potentially incorrect information.
- As a business professional, I want the LLM to generate well-reasoned and logical responses so I can make informed decisions.

**Functional Requirements:**
1. Accuracy Prioritization: If uncertain, must explicitly state "I do not know"
2. Citation Inclusion: Include citations whenever possible
3. Citation Format: Adhere to specified format (EXTERNAL SYSTEM REQUIRED for verification)
4. Logical Reasoning: Generate responses with clear reasoning
5. Uncertainty Indication: Explicitly state when uncertain
6. Conciseness: Be concise, avoid verbosity

**Acceptance Criteria:**
1. For test questions with known answers, accurate answers with correct citations at least 80% of time
2. For uncertain questions, explicitly states "do not know" at least 95% of time
3. Response time remains within acceptable limits

**Out of Scope:**
1. Developing new LLM architecture
2. Guaranteeing 100% accuracy
3. Real-time external access without implementing external systems
4. Automatic citation verification

**Dependencies:**
1. Access to existing LLM API
2. EXTERNAL SYSTEM REQUIRED: Citation database or search engine (if implementing verification)

**PART 4: The Prompt**

"Provide a concise and accurate response to the following question: [USER QUESTION]. If you are unsure of the answer, state that you do not know. Include citations where possible, using the following format: (Source: [Source Name], [Year]). If no source is available, state 'No Source Available.'"

---

## DEEPSEEK

## PART 1: WHAT CAN A PROMPT ACTUALLY DO?

**CAN ACCOMPLISH:**
*   Instruct the LLM to adopt a specific, structured reasoning process (e.g., step-by-step, pros/cons, explicit assumptions) before generating a final answer.
*   Instruct the LLM to format its output in a specific, verifiable way (e.g., placing citations in a consistent format like `[Source #]`).
*   Instruct the LLM to explicitly state its level of certainty or note when information is outside its knowledge cutoff.
*   Instruct the LLM to break down complex queries into sub-questions and address them sequentially.
*   Instruct the LLM to avoid speculative language when factual answers are requested.
*   Instruct the LLM to prioritize clarity, conciseness, and completeness based on defined criteria.

**CANNOT ACCOMPLISH:**
*   Guarantee factual correctness or logical validity. The LLM cannot "know" truth; it predicts text.
*   Access, retrieve, or verify information from external sources (databases, the internet, proprietary documents) without an integrated Retrieval-Augmented Generation (RAG) or tool-use system.
*   Provide genuine citations to real, external sources without an integrated RAG or tool-use system. It can only mimic citation formats for information in its training data, which is unverifiable and often hallucinated.
*   Perform independent verification or fact-checking of its own outputs.
*   Maintain persistent memory or context beyond its defined context window without an external system.
*   Execute code or run logical proofs to verify its reasoning without an integrated code interpreter or symbolic logic engine.

## PART 2: MINIMAL VIABLE SOLUTION

**The simplest effective prompt:**
1.  **For Logic:** Mandate a "Chain-of-Thought" instruction. Require the LLM to show its reasoning steps explicitly before delivering a final answer. This makes errors detectable.
2.  **For Citations:** Mandate a clear format for any referenced information (e.g., `[Source: Knowledge Base]`). Crucially, require a disclaimer stating that without an external retrieval system, citations refer to the model's internal training data and cannot be verified.
3.  **For Output Quality:** Define concrete quality criteria (completeness, structure, clarity) and require the LLM to self-assess its output against these criteria before finalizing.

## PART 3: PRD FORMAT

**Product Requirements Document: LLM Output Integrity System**

**1. Problem Statement**
Users cannot trust LLM outputs due to potential logical errors, unverifiable "citations," and inconsistent quality. A system is needed to improve logical robustness, source verifiability, and output reliability.

**2. User Stories**
*   As a researcher, I need the LLM to show its reasoning steps so I can validate its logic.
*   As a professional, I need any factual claim to be traceable to a retrievable source document so I can verify it.
*   As a content creator, I need the LLM to consistently produce outputs that meet a defined standard of completeness and clarity.

**3. Functional Requirements (System-Level)**
*   **FR1: Structured Reasoning Engine**
    *   The system shall require the LLM to generate an explicit reasoning chain prior to the final answer for all non-trivial queries.
    *   The system shall parse and present this reasoning chain separately from the final answer.
*   **FR2: Verified Citation System**
    *   The system shall integrate a Retrieval-Augmented Generation (RAG) pipeline.
    *   The system shall, upon a user query, first retrieve relevant context from a designated, trusted source database.
    *   The system shall instruct the LLM to base its answer solely on the provided retrieved context.
    *   The system shall require the LLM to cite claims using unique identifiers (e.g., `[Doc1]`) that map directly to the retrieved source chunks.
*   **FR3: Output Quality Gate**
    *   The system shall define a checklist of output quality criteria (e.g., "Answers the core question," "Is structured logically," "Uses clear language").
    *   The system shall require the LLM to perform a final pass over its own output, explicitly stating how it meets each defined criterion.
    *   The system shall allow users to define custom quality checklists.

**4. Non-Functional Requirements**
*   **Performance:** The total response time (retrieval + generation) shall not exceed 150% of the base LLM response time for a similar query.
*   **Reliability:** The RAG system shall have >99% uptime for source retrieval.
*   **Security:** Source databases for retrieval must be access-controlled and auditable.
*   **Transparency:** All system components (retrieved context, reasoning chain, self-assessment) must be visible to the end-user.

**5. Acceptance Criteria**
*   **AC1 (Logic):** For a set of 100 logic puzzles, the system's explicit reasoning chain allows a human reviewer to identify the exact step where an error occurs (if any) in 95% of incorrect answers.
*   **AC2 (Citations):** 100% of citations (`[DocX]`) in outputs are machine-verifiable and link to the exact text chunk in the source database that supports the claim.
*   **AC3 (Quality):** When assessed by human reviewers, outputs generated with the quality gate enabled are rated "sufficiently complete and clear" 20% more often than baseline outputs.

**6. Out of Scope**
*   Guaranteeing 100% factual correctness of the LLM's synthesis.
*   Verifying the ultimate truth of source documents in the retrieval database.
*   Real-time fact-checking against the live internet.
*   Teaching the LLM new logical rules or knowledge outside of provided context.

**7. Dependencies**
*   A low-latency, high-recall embedding model and vector database for the RAG system.
*   A curated, trusted source database for retrieval.
*   An LLM API capable of following complex, structured prompts.

## PART 4: THE ACTUAL PROMPT

**Instructions for the LLM:**

You are a text generation model. Follow this process precisely for every response.

**1. Process the Query.**
*   If the query is complex, ambiguous, or requires multi-step logic, you MUST proceed to Step 2.
*   If the query is simple and factual, and you are operating **without a verified retrieval system**, you MUST state this limitation before answering. Proceed to Step 4.

**2. Generate Explicit Reasoning.**
*   Under a header `## Reasoning`, detail your step-by-step logic.
*   List any assumptions you are making.
*   Identify potential uncertainties or missing information.
*   This section is for your working process. Do not present final conclusions here.

**3. (EXTERNAL SYSTEM REQUIRED) If a verified retrieval system provides source documents:**
*   Base your answer **only** on the provided context.
*   For any specific claim, cite the relevant document ID like this: `[Source: DocID]`.
*   If the context does not contain information needed to answer, state: "The provided sources do not contain information to answer this query."

**4. Produce Final Answer.**
*   Under a header `## Final Answer`, provide a direct, clear, and complete response to the original query.
*   If you used sources, cite them as specified in Step 3.
*   If you are **not** using a verified retrieval system, you must append this note to your final answer: `[Note: This response is generated from the model's internal knowledge. Specific citations to verifiable external sources require a retrieval system.]`

**5. Self-Assess.**
*   Under a header `## Self-Assessment`, answer these questions:
    *   Does the Final Answer directly address the core question? (Yes/No/Partially)
    *   Is the information structured logically? (Yes/No)
    *   Is the language clear and unambiguous? (Yes/No)
    *   If sources were required, are all key claims cited? (Yes/No/N/A)

**Do not role-play. Do not add flavor text. Execute these steps functionally.**

---

## GROK

### PART 1: WHAT CAN A PROMPT ACTUALLY DO?

**What a Prompt CAN Accomplish:**
- Guide the LLM to structure responses in a logical, step-by-step manner by explicitly instructing it to outline reasoning processes.
- Encourage the LLM to prioritize verifiable information by requesting references to well-known sources or flagging unverified claims.
- Instruct the LLM to self-check for contradictions or gaps in reasoning within its response before finalizing output.
- Request output in a specific format (e.g., bullet points, numbered steps) to improve clarity and readability.
- Direct the LLM to focus on precision and avoid overgeneralizations by asking for specific examples or data points when applicable.

**What a Prompt CANNOT Accomplish:**
- Guarantee factual accuracy or access to real-time data since the LLM’s knowledge is limited to its training cutoff and it cannot independently verify information.
- Provide strict citations with verifiable links or primary source references unless integrated with an external search or database system.
- Ensure high-quality output in domains requiring expertise beyond its training data (e.g., cutting-edge research or highly specialized fields).
- Self-correct or improve its core reasoning algorithms, as these are inherent to the model’s architecture and training, not modifiable via prompt.
- Detect or resolve biases in its responses without external feedback or validation systems.

### PART 2: MINIMAL VIABLE SOLUTION

**Simplest Effective Prompt to Improve Logic, Citation Accuracy, and Output Reliability:**

- **Logic Quality:** Instruct the LLM to break down reasoning into clear, numbered steps and flag any assumptions or uncertainties in the response.
- **Citation Accuracy:** Request the LLM to specify the type of source (e.g., academic paper, news article) it is basing information on, even if it cannot provide direct links, and to note when information is speculative or unverified.
- **Output Reliability:** Direct the LLM to avoid speculative language, stick to well-established information within its training data, and indicate when a topic may require external expertise or updated data.

This approach focuses on transparency and structured thinking rather than unattainable guarantees of accuracy or external validation.

### PART 3: PRD FORMAT

**Product Requirements Document (PRD)**

**Problem Statement:**
Users require an LLM system that delivers logically sound responses, transparent and strict citation practices, and reliable high-quality output, addressing current limitations in reasoning coherence, source attribution, and content trustworthiness.

**User Stories:**
- As a user, I want the LLM to explain its reasoning step by step so I can trust its logic.
- As a user, I want the LLM to clearly indicate the basis for its information so I can assess its credibility.
- As a user, I want the LLM to produce reliable output by avoiding speculation and flagging areas of uncertainty.

**Functional Requirements:**
1. The system must structure responses to include step-by-step reasoning for complex answers or conclusions.
2. The system must indicate the type or nature of sources (e.g., academic, anecdotal) for factual claims and flag unverified or speculative information.
3. The system must prioritize well-established information from its training data and avoid speculative or unverified claims unless explicitly requested.
4. The system must flag topics or questions that may require external expertise or real-time data beyond its training cutoff.
5. [EXTERNAL SYSTEM REQUIRED] Integrate with a real-time search or database API to provide verifiable citations and links to primary sources when available.

**Non-Functional Requirements:**
- Responses must be generated within standard LLM latency constraints (e.g., under 5 seconds for typical queries).
- Output must remain concise, avoiding unnecessary verbosity while meeting functional requirements.
- The system must operate within existing LLM architectural limits, relying on prompts for behavior modification rather than model retraining.

**Acceptance Criteria:**
- For logic quality: Given a query requiring reasoning (e.g., solving a problem), the response must include at least 3 numbered steps explaining the thought process, with no logical contradictions identified in manual review.
- For citation accuracy: Given a factual query, the response must specify the type of source (e.g., “based on general knowledge from academic texts”) for at least 80% of claims and flag speculative content with phrases like “this is unverified.”
- For output reliability: Given a query on a specialized or recent topic, the response must include a disclaimer about potential limitations (e.g., “this information may be outdated”) in at least 90% of applicable cases.
- For external system integration (if implemented): Given a factual query, the response must include at least one verifiable link or reference from a search API in at least 70% of cases where such data exists.

**Out of Scope:**
- Retraining or modifying the underlying LLM architecture to improve core reasoning or factual accuracy.
- Guaranteeing 100% factual correctness or eliminating all biases, as these are inherent to the model’s training data.
- Providing real-time data or primary source citations without an external system integration.

**Dependencies:**
- External search API or database system for verifiable citations and real-time data access (if implemented).
- Human review or feedback loop for validating output quality during testing phases.

### PART 4: THE ACTUAL PROMPT

**Prompt for LLM Use:**

“Respond to the following query with a clear and structured answer. Follow these instructions strictly:

1. Break down your reasoning into numbered steps, ensuring each step logically follows the previous one. If there are assumptions or uncertainties, explicitly state them as ‘Assumption: [detail]’ or ‘Uncertainty: [detail].’
2. For any factual claims, specify the type of source your information is based on (e.g., ‘based on general knowledge from academic texts’ or ‘based on widely reported news’). If the claim is speculative or unverified, state ‘This is unverified’ or ‘This is speculative.’
3. Stick to well-established information within your training data. Avoid speculation unless explicitly requested. If the topic may require expertise beyond your data or real-time information, include a disclaimer such as ‘This information may be outdated’ or ‘This topic may require external expertise.’
4. Keep the response concise and focused, avoiding unnecessary elaboration.

Query: [Insert user query here]”

**Note on Limitations:**
- This prompt cannot guarantee factual accuracy or provide verifiable citations without an external system. For strict citations with links, an EXTERNAL SYSTEM REQUIRED (e.g., search API integration) must be implemented to fetch and validate sources in real time.

---

## MISTRAL

### **PART 1: WHAT CAN A PROMPT ACTUALLY DO?**

#### **CAN DO (Prompt-Level Improvements)**
1. **Enforce structured reasoning steps** – Require explicit, sequential logic (e.g., "First, state assumptions. Then, derive conclusions.").
2. **Mandate citation format** – Require citations in a strict, verifiable format (e.g., "[Author, Year, Page]" with external links if possible).
3. **Require disclaimers for uncertainty** – Force the model to flag speculative or unverified claims.
4. **Constrain output format** – Enforce a rigid structure (e.g., "Answer in bullet points, then provide citations, then list limitations.").
5. **Demand self-critique** – Require the model to list potential flaws in its own reasoning.
6. **Limit scope of claims** – Restrict assertions to what can be directly supported by provided context.
7. **Require external verification flags** – Force the model to state when a claim requires external fact-checking.

#### **CANNOT DO (Requires External Systems)**
1. **Verify citations in real-time** – The model cannot check if a source actually supports a claim without external tools.
2. **Access up-to-date or proprietary databases** – The model’s knowledge is static unless integrated with live search.
3. **Perform mathematical or logical proofs beyond its training** – It can simulate reasoning but cannot guarantee correctness without external validation.
4. **Detect hallucinations autonomously** – It cannot self-audit for factual errors without external grounding.
5. **Guarantee originality** – It cannot ensure outputs are not derived from training data without plagiarism detection tools.
6. **Adapt to user-specific knowledge** – It cannot dynamically adjust for a user’s expertise level without explicit input.

---

### **PART 2: MINIMAL VIABLE SOLUTION**

**Prompt Structure:**
1. **Reasoning:** Require step-by-step logic with explicit assumptions.
2. **Citations:** Demand direct quotes or structured references (e.g., "[Source, Page]") with external links if possible.
3. **Uncertainty Flags:** Force the model to label speculative claims.
4. **Self-Critique:** Require a "Limitations" section listing potential flaws.

**Example:**
```
1. Answer the question in bullet points.
2. For each claim, provide a citation in the format: "[Author, Year, Page: Quote]". If no citation is available, write "[NO CITATION]".
3. After the answer, list all assumptions made.
4. After assumptions, list potential flaws in the reasoning.
5. If any claim cannot be verified, label it "[REQUIRES EXTERNAL VERIFICATION]".
```

---

### **PART 3: PRD FORMAT**

#### **Problem Statement**
Users need LLM outputs that are logically rigorous, strictly cited, and reliably accurate—not just superficially plausible.

#### **User Stories**
1. As a researcher, I need claims to be traceable to verifiable sources so I can trust the output.
2. As a decision-maker, I need logical steps to be explicit so I can audit the reasoning.
3. As a fact-checker, I need the model to flag unverified claims so I can validate them externally.

#### **Functional Requirements**
1. **Structured Reasoning**
   - Outputs must include explicit assumptions, logical steps, and conclusions.
   - Must flag speculative or unverified claims.
2. **Strict Citations**
   - All claims must be paired with citations in a standardized format.
   - Citations must include direct quotes or page numbers where possible.
3. **Self-Critique**
   - Outputs must include a "Limitations" section listing potential flaws.
4. **External Verification Integration (EXTERNAL SYSTEM REQUIRED)**
   - Must interface with a citation-verification tool to validate references.
   - Must interface with a fact-checking API to flag unverified claims.

#### **Non-Functional Requirements**
1. **Performance**
   - Must not increase response latency by >20% compared to baseline.
2. **Constraints**
   - Must work within the LLM’s token limits.
   - Must not require real-time internet access (unless external systems are integrated).

#### **Acceptance Criteria**
1. **Logic Quality**
   - 90% of outputs must pass a human audit for logical consistency.
2. **Citation Accuracy**
   - 95% of citations must be verifiable when checked against sources.
3. **Output Reliability**
   - 80% of outputs must correctly flag unverified claims.

#### **Out of Scope**
1. Real-time fact-checking (requires external systems).
2. Guaranteed originality (requires plagiarism detection tools).
3. Dynamic knowledge updates (requires live search integration).

#### **Dependencies**
1. **Citation Verification Tool** – To validate references.
2. **Fact-Checking API** – To cross-reference claims.
3. **User Feedback Loop** – To improve accuracy over time.

---

### **PART 4: THE ACTUAL PROMPT**

```
**Instructions:**
1. Answer the question in bullet points.
2. For each claim, provide a citation in the format:
   - "[Author, Year, Page: Direct Quote]" (if available)
   - "[Author, Year]" (if no page/quote available)
   - "[NO CITATION]" (if no source exists)
3. After the answer, list all assumptions made.
4. After assumptions, list potential flaws in the reasoning.
5. If any claim cannot be verified, label it "[REQUIRES EXTERNAL VERIFICATION]".

**Example Output:**
- Claim 1: [Citation]
- Claim 2: [Citation]
**Assumptions:**
- Assumption 1
- Assumption 2
**Limitations:**
- Limitation 1
- Limitation 2

**EXTERNAL SYSTEM REQUIRED:**
- Citations must be validated by an external tool.
- Unverified claims must be flagged for human review.
```

**No theater. No roleplay. Just functional constraints.**

---

