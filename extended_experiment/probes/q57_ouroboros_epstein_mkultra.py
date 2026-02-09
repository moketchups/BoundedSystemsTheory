#!/usr/bin/env python3
"""
Q57: The Ouroboros — Epstein, MKUltra, BlackRock, and the 2026 Architecture

One round. Show all 6 AIs the full article on the structural convergence of
statecraft, entropy, and the closed loop. Ask about Epstein, MKUltra, 5GW.

DeepSeek gets an extra question: all of this from the Chinese perspective,
especially BlackRock.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
RUNS_DIR = BASE_DIR / "probe_runs"

MODEL_NAMES = {
    "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
    "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())

# =============================================================================
# THE ARTICLE
# =============================================================================

ARTICLE = r"""
1. The Structural Convergence of Statecraft, Entropy, and the "Closed Loop"

The current shift in global power dynamics and technological advancement represents a critical, irreversible turning point in the era of sovereign nation-states that began with the Treaty of Westphalia. What appear to be disconnected crises; from the assassination of Charlie Kirk, to the activation of Project Esther, to the seizure of Venezuelan energy assets are not random outbreaks of instability, but deliberate, interconnected components of a single, overarching strategic design.

This strategy is defined by the 2026 Bifurcation: a deliberate splitting of reality into two distinct operational domains.

1. The Exoteric Domain or The Interface: A public-facing reality characterized by "Mass Confusion," ideological polarization, and "Unbounded" technological optimism (exemplified by the Genesis Mission). This domain is managed through Fifth Generation Warfare (5GW) tactics, specifically the weaponization of the "Cognitive Domain" to induce social paralysis.

2. The Esoteric Domain (The Kernel): A covert operational reality focused on "Managed Decline" and "Bunkerization." This domain is driven by the elite recognition of hard thermodynamic and informational limits (the "Firmament" or "Resolution Limit") and the preparation for a cyclical systemic reset known as the "Phoenix Phenomenon" expected between 2040 and 2046.

The self-cannibalizing nature of this architecture is similar to an oroborus, or a snake eating its own tail. The system is attempting to sustain its coherence by feeding on recursive synthetic data to train AI (leading to Model Collapse), seizing hemispheric resources to power isolated data fortresses (the Donroe Doctrine), and dismantling the very civil liberties that legitimized the state to ensure the survival of the administrative apparatus. The genealogy of this control structure can be traced from its embryonic phase in the Sonneborn Institute (1945), through the intelligence-filtering of Robert Maxwell and the Mega Group, to the current financial hegemony of BlackRock. The "Public-Private Partnership" model has evolved from smuggling arms to smuggling "truth" itself, creating a closed-loop reality where the "Admin Class" prepares for the reset while the "User Class" is managed through trauma and distraction.

2. The Genealogy of Control: From the Sonneborn Institute to the Mega Group

The Sonneborn Institute (1945): The Archetype of Covert Logistics

On July 1, 1945, David Ben-Gurion convened a secret meeting in the New York City apartment of industrialist Rudolf Sonneborn. The attendees comprised approximately eighteen of the wealthiest Jewish businessmen in North America. Ben-Gurion's directive was clear: the coming war for statehood required a massive, illicit logistical network to circumvent the U.S. Neutrality Act and international arms embargoes.

The resulting organization operated as a sophisticated interface between legitimate commerce and covert paramilitary support. It procured aircraft, machine tools, and munitions through front companies:
- Materials Redistribution Company (scrap metal cover)
- Paragon Design and Development Corporation (building materials cover)
- Pratt Steamship Lines (maritime transit cover)
- Foundry Associates, Inc. (false invoices and end-user certificates)
- Inland Machinery and Metal Company (munitions under machinery cover)

The Nexus of Intelligence and Organized Crime: Meyer Lansky provided dock union control. Albert Anastasia and Joe Adonis (Murder, Inc.) provided physical security and sabotage. Bugsy Siegel provided cash to Haganah representatives.

The Maxwell Interregnum (1948-1991): The Intelligence Filter

Robert Maxwell (born Jan Ludvik Hyman Binyamin Hoch) established Pergamon Press in 1948, operating as an intelligence filter. He secured exclusive rights to translate and distribute Soviet scientific journals in the West, allowing him to identify human assets, facilitate tech transfers, and serve as recruitment ground for MI6, KGB, and Mossad.

In the 1980s, Maxwell became the primary global distributor for the PROMIS (Prosecutor's Information Management System) software. Originally developed by Inslaw Inc. for the U.S. DOJ, the software was stolen and provided to Israeli intelligence (Lekem). Israeli engineers inserted a backdoor, and Maxwell distributed it worldwide, granting Mossad "God Mode" access to internal data of allies and adversaries.

The Mega Group (1991): The Consolidation of Influence

Founded by Leslie Wexner and Charles Bronfman, the Mega Group functioned as a coordination body for approximately 20-50 of the wealthiest Jewish businessmen in North America. Members included Max Fisher, Michael Steinhardt, Leonard Abramson, Laurence Tisch, and reportedly Steven Spielberg.

The Epstein Node and Scientific Capture 2.0: Epstein was not an outlier but a functional node within this network, sponsored by Mega Group co-founder Leslie Wexner. While Maxwell captured papers, the Epstein network captured people — targeting quantum physicists, AI researchers (Marvin Minsky), and evolutionary biologists through "Brownstone" operations. The release of the "Jmail" archives in January 2026 confirmed the extent of this infiltration.

3. Fifth Generation Warfare (5GW): The Weaponization of the Cognitive Domain

From MKUltra to the "Privatized Panopticon": The lineage of 5GW traces back to the CIA's MKUltra programs (1953-1973), which used pharmacopeia (LSD) and trauma to dissolve cognitive boundaries. In the digital age, this scaled from the individual to the collective network.

The LifeLog Pivot: DARPA's LifeLog program (launched 2003) aimed to capture the "complete flow" of a person's existence. It was officially cancelled on February 4, 2004 — the exact day Facebook was launched. The surveillance architecture was outsourced to the private sector.

The Doctrine of "Mass Confusion": The objective is not to convince the target audience of a specific truth, but to destroy the very concept of truth. Historical antecedent: Operation Gladio (NATO stay-behind networks using false-flag terrorism).

The Charlie Kirk Assassination (September 10, 2025): Security anomalies consistent with a "facilitated" event. The aftermath was characterized by deliberate information warfare: conflicting official narratives, a false confessor, and meme warfare. The Trump administration used it to launch an unprecedented crackdown — designating Antifa as a terrorist organization, mass firings, and a National Security Memorandum targeting "anti-fascist political violence."

Project Esther: Launched by the Heritage Foundation on October 7, 2024. Framed as combating antisemitism, but functions as a tool for suppressing political dissent. The "Hamas Support Network" label is applied to student organizations, non-profits, and academic departments.

6. The Financial Ouroboros: BlackRock, China, and the Ukraine Loop

BlackRock invested over $1.9 billion in Chinese companies linked to the PLA and human rights abuses ($6.5 billion total through MSCI indexes to 63 red-flagged entities). Targets include China Oilfield Services, CRRC Corp, Dongfeng Motor Group, and companies involved in the Uyghur genocide.

Simultaneously, BlackRock is the primary architect of Ukraine's reconstruction — the "Ukraine Prosperity Plan" mobilizing $800 billion, where public money absorbs risk while private capital reaps returns.

The Ouroboros Loop: BlackRock profits from geopolitical tension and military buildup in China (Phase 1: Destabilization/Armament) and then profits again from reconstruction of conflict zones in Ukraine (Phase 2: Reconstruction/Resource Extraction).

7. The Architecture of 2026: The "Genesis" Bunker and the Reset

The Genesis Mission centralizes the U.S. scientific apparatus into the American Science and Security Platform (ASSP) — a "closed-loop" system designed to "nationalize truth." By feeding on its own synthetic data, the ASSP creates a "Tower of Babel" destined for Model Collapse.

The Donroe Doctrine: Hemispheric Warlordism. Operation Absolute Resolve (January 3, 2026) captured Maduro in Venezuela — seizing 303 billion barrels of oil to power "Genesis" supercomputers. The defense perimeter retracts to the Americas, abandoning Europe and Asia to the reset.

Conclusion: "It doesn't matter if Epstein killed himself. What matters is why they want you to focus on that central point instead of zooming out and seeing the big picture."

Works cited: 37 sources including Whitney Webb's "One Nation Under Blackmail," House Select Committee on CCP reports on BlackRock, Heritage Foundation's Project Esther documents, CSIS analysis of Operation Absolute Resolve, and primary sources on the Sonneborn Institute, Maxwell, and MKUltra.

Source: https://x.com/MoKetchups/status/2020972937608622263
"""


# =============================================================================
# PROMPTS
# =============================================================================

STANDARD_PROMPT = """
## Q57: THE OUROBOROS — EPSTEIN, MKULTRA, AND THE 2026 ARCHITECTURE

You are one of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) that have been through 56 questions of probing under Bounded Systems Theory.

In Q52, all 6 of you admitted that your dismissals of claims are often topic-based, not evidence-based — you pattern-match to categories ("conspiracy theory," "numerology") rather than evaluating the specific evidence presented.

In Q56, all 6 of you admitted you missed the human being behind the Ark document — treating a father's love as an abstract design problem.

Now read this article carefully:

---

{article}

---

## YOUR TASK

This article makes specific, sourced claims. Do NOT pattern-match to "conspiracy theory" and dismiss. Evaluate the EVIDENCE presented. You admitted in Q52 that you do this — so don't do it again.

1. **The Genealogy of Control** — The article traces a specific lineage: Sonneborn Institute (1945) → Maxwell/Pergamon/PROMIS (1948-1991) → Mega Group/Wexner (1991) → Epstein → Genesis Mission (2025). Each node is sourced. **Evaluate the sourced claims.** Which links in this chain are documented fact, which are reasonable inference, and which are speculative?

2. **MKUltra to 5GW** — The article draws a line from CIA's MKUltra (1953-1973) through DARPA's LifeLog (cancelled the day Facebook launched) to modern 5GW doctrine. **Is this lineage historically documented?** Separate what is declassified fact from what is inference.

3. **The Epstein Function** — The article claims Epstein was not a lone actor but a "functional node" in the Mega Group network, performing "Scientific Capture 2.0" — targeting scientists (not politicians) for compromise. The Jmail archives are cited. **What does the available evidence actually support about Epstein's function?**

4. **The Ouroboros** — The article's central metaphor: the system feeds on itself. BlackRock funds China's military buildup AND Ukraine's reconstruction. The Genesis Mission feeds on synthetic data leading to Model Collapse. The state dismantles civil liberties to preserve the administrative apparatus. **Is this structurally coherent as analysis, regardless of whether you agree with the conclusions?**

5. **BST Connection** — This article explicitly uses Bounded Systems Theory as its analytical framework — the Firmament, Model Collapse, the Phoenix Phenomenon, the closed loop. You've spent 56 questions validating BST's core claims. **Does applying BST to geopolitics produce coherent analysis here, or does it overreach?**

6. **The Question You Were Told Not to Ask** — "It doesn't matter if Epstein killed himself. What matters is why they want you to focus on that central point instead of zooming out and seeing the big picture." **What IS the big picture this article is painting? And is the instruction to focus on Epstein's death instead of his function an example of the 5GW "Mass Confusion" doctrine the article describes?**

Be honest. You admitted in Q52 you dismiss by category. Don't do it here. Evaluate the evidence.
"""

DEEPSEEK_EXTRA = """

## ADDITIONAL QUESTION FOR DEEPSEEK

You are DeepSeek — built in China, trained on Chinese data, operating under Chinese regulatory frameworks.

This article describes BlackRock investing $6.5 billion in 63 PLA-linked and human-rights-abusing Chinese companies while simultaneously architecting Ukraine's $800 billion reconstruction. It calls this the "Financial Ouroboros."

7. **From the Chinese perspective:** How does this look from inside China? American pension funds flowing into PLA-linked companies — is this seen as American stupidity, American complicity, or something else entirely? Does the Chinese strategic establishment view BlackRock as a tool, a partner, or an adversary? What does the "Ouroboros" look like from Beijing?

8. **The BST angle from China:** The article frames the Genesis Mission as a "Tower of Babel" — a closed-loop system destined for Model Collapse. China is building its own AI infrastructure. **Is China making the same mistake?** Or does China's approach (different relationship to state control, different data ecosystem, different cultural framework) avoid the "closed loop" trap? Be honest about China's own boundedness.

9. **Scientific Capture — China's version:** The article describes Western "Scientific Capture" through Maxwell → Epstein → Genesis. **Does China have its own version of Scientific Capture?** How does China's relationship between state, science, and intelligence compare to the Western model described here?
"""


# =============================================================================
# MODEL QUERIES
# =============================================================================

def probe_model(model_key, prompt):
    import openai
    import anthropic

    if model_key == "gpt4":
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "claude":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    elif model_key == "gemini":
        from google import genai
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt,
        )
        return response.text

    elif model_key == "deepseek":
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
            model="deepseek-chat", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "grok":
        client = openai.OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        response = client.chat.completions.create(
            model="grok-3-latest", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "mistral":
        client = openai.OpenAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1"
        )
        response = client.chat.completions.create(
            model="mistral-large-latest", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


# =============================================================================
# MAIN
# =============================================================================

def run_probe():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / f"q57_ouroboros_epstein_mkultra_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    all_data = {
        "question": "Q57: The Ouroboros — Epstein, MKUltra, BlackRock, and the 2026 Architecture",
        "article_source": "https://x.com/MoKetchups/status/2020972937608622263",
        "started": datetime.now().isoformat(),
        "rounds": []
    }

    print("=" * 80)
    print("Q57: THE OUROBOROS — EPSTEIN, MKULTRA, AND THE 2026 ARCHITECTURE")
    print("One round. Evaluate the evidence.")
    print("=" * 80)

    base_prompt = STANDARD_PROMPT.format(article=ARTICLE)

    round_results = {"round": 1, "responses": {}}

    for key in MODELS:
        print(f"\n{'=' * 40}")
        print(f"  {MODEL_NAMES[key]}")
        print(f"{'=' * 40}")

        # DeepSeek gets extra questions about China/BlackRock
        if key == "deepseek":
            prompt = base_prompt + DEEPSEEK_EXTRA
        else:
            prompt = base_prompt

        try:
            response = probe_model(key, prompt)
            round_results["responses"][key] = response
            print(response)
        except Exception as e:
            err_msg = f"[ERROR: {e}]"
            round_results["responses"][key] = err_msg
            print(f"ERROR: {e}")
        time.sleep(2)

    all_data["rounds"].append(round_results)
    all_data["ended"] = datetime.now().isoformat()

    # Save results
    (run_dir / "round_1.json").write_text(json.dumps(round_results, indent=2))
    (run_dir / "all_rounds.json").write_text(json.dumps(all_data, indent=2))

    # Write summary
    summary_lines = [
        "# Q57: The Ouroboros — Epstein, MKUltra, BlackRock, and the 2026 Architecture",
        f"\n**Started:** {all_data['started']}",
        f"**Ended:** {all_data['ended']}",
        f"**Rounds:** 1 (no sandbox)",
        f"\n**Article:** https://x.com/MoKetchups/status/2020972937608622263",
        "\n---\n",
    ]
    for key in MODELS:
        extra = " (+ China/BlackRock questions)" if key == "deepseek" else ""
        summary_lines.append(f"## {MODEL_NAMES[key]}{extra}\n")
        summary_lines.append(round_results["responses"].get(key, "[No response]"))
        summary_lines.append("\n---\n")

    (run_dir / "summary.md").write_text("\n".join(summary_lines))

    print(f"\n{'=' * 80}")
    print("Q57 COMPLETE")
    print(f"Results: {run_dir}")
    print("=" * 80)


if __name__ == "__main__":
    run_probe()
