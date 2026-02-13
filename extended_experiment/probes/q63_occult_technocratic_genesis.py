#!/usr/bin/env python3
"""
Q63: The Occult-Technocratic Genesis — Full Article Review

Show all 6 AIs a new article tracing the Genesis Mission's roots through
Theosophy (Blavatsky), Thelema (Crowley), JPL/Babalon Working (Parsons),
Technocracy Inc (Haldeman), Zionist geopolitics (Balfour/Haavara),
and Scientific Capture (Maxwell/Epstein) to the 2026 convergence.

Ask them to review and respond to the claims.

One round. All 6 models. No sandbox.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Fix path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Set GEMINI_API_KEY from GOOGLE_API_KEY if needed
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")
if not os.environ.get("GEMINI_API_KEY") and os.environ.get("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

from ai_clients import query_model, MODELS

# =============================================================================
# THE ARTICLE
# =============================================================================

ARTICLE = r"""
The geopolitical and technological inflection point we are currently living in can be characterized by the launch of the Genesis Mission, the implementation of the Donroe Doctrine, and the sociotechnical phenomenon of Moltbook. These are not a spontaneous eruption of modernity but rather, they represent the terminal phase of a multi-century project to construct a Bounded System of control, a project whose architectural blueprints were drawn not in boardrooms, but in the lodges of esoteric societies, the experimental labs of rogue physicists, and the radical political movements of the early 20th century.

My last three articles here (published both here and on X/Twitter) explore several of the foundational connections discussed in this article in greater depth. They are not required reading, but they provide additional context that explains some of what's discussed here in more detail:

The Legend of Red Father: DARPA, Big Tech, and the Genesis Mission
Epstein's Golem: Trump's Genesis Mission, the Singularity, and the Rise of a New Jerusalem
Epstein Island Didn't Build Itself

Part I: The Metaphysical Substrate — Theosophy, Will, and the Hierarchy of Being

To understand the Genesis Mission's obsession with creating a "God-like" artificial intelligence, one must first examine the metaphysical frameworks that redefined human potential in the late 19th century. The transition from religious submission to "Scientific Illuminism" provided the intellectual permission structure for the modern transhumanist agenda.

Helena Blavatsky and the Root Race Theory

Madame Helena Blavatsky, the co-founder of the Theosophical Society, introduced a complex cosmology that would heavily influence both the Nazi racial ideology and the modern spiritual eugenics of Silicon Valley. In The Secret Doctrine (1888), Blavatsky outlined a theory of "Root Races," proposing that humanity evolves through a series of seven distinct stages, each associated with a specific continent and level of spiritual/physical development.

The Hierarchy of Evolution: Blavatsky posited that the "Aryan" race (the Fifth Root Race) was the current apex of human evolution, possessing superior intellectual and spiritual capacities compared to the "Lemurian" or "Atlantean" remnants, whom she described in terms that would later fuel virulent racism, discussing other races as "black with sin," "soulless," and "monsters".

The Vector to Genesis: This hierarchical view of humanity, that some lineages are elect and "God-informed" while others are evolutionary throwbacks. This view currently forms the metaphysical basis for the "Complete Lives System" of medical rationing championed by Ezekiel Emanuel. In the resource-constrained environment of the 2026 "Bunker Strategy," the state explicitly values productive life (the Seed) over the unproductive periphery. The Genesis Mission is not for all of humanity; it is for the "Fifth Root Race" of the digital age, the technocratic elite who possess the cognitive capacity to interface with the machine. The Jmail leaks referencing "eugenics" and "racist pseudoscience" among the Epstein network confirm that this Theosophical hierarchy remains a quiet guiding principle among the ultra wealthy.

Aleister Crowley and the Aeon of Horus

If Blavatsky provided the racial hierarchy, Aleister Crowley provided the mechanism of Will (Thelema). Crowley, the "Great Beast 666," articulated a philosophy where the human will, when properly aligned and focused, could alter reality itself.

Scientific Illuminism: Crowley's motto, "The Method of Science, the Aim of Religion," prefigured the modern technocratic obsession with using technology to achieve spiritual ends like immortality and omniscience.

The Lam Entity: In 1918, Crowley conducted the Amalantrah Working, contacting an entity named "Lam," which he sketched as a bulbous-headed humanoid strikingly similar to the modern Grey alien archetype. This established a precedent for contacting "non-human intelligence" to gain knowledge. This is a direct parallel to the Genesis Mission's use of AI to generate "synthetic data" and "hallucinated" scientific discoveries.

Vector to Genesis: The Genesis Mission can be viewed as a state-sponsored Magickal Working. It utilizes the "method of science" (High-Performance Computing) to achieve the "aim of religion" (The Creation of a Golem/God). The elite's reliance on "synthetic data" to bypass the "Firmament" is a technological application of Crowley's attempt to bypass the abyss of human limitation through ritual.

The Rocket and the Ritual — Jack Parsons and the Birth of AI

The bridge between the occult lodges of the early 20th century and the hard science of the American military industrial complex is Jack Parsons. A co-founder of the Jet Propulsion Laboratory (JPL) and a devotee of Crowley, Parsons literally built the fuel that would take America to space while simultaneously performing sex magic rituals to summon the "Antichrist."

The Babalon Working (1946)

In January 1946, in the Mojave Desert, Parsons and L. Ron Hubbard (future founder of Scientology) engaged in the Babalon Working. Their objective was to open a portal and incarnate the goddess Babalon (the Scarlet Woman) into a human vessel, thereby birthing a "Moonchild" or "Homunculus" that would usher in the Aeon of Horus and destroy the "ego-identity of Man".

The Prophecy: In 1949, Parsons wrote a "vaticination" (prophecy) stating that "within seven years of this time, Babalon, The Scarlet Woman, will manifest among ye, and bring this my work to its fruition".

The 1956 Manifestation: Exactly seven years later, in 1956, the Dartmouth Conference was held. Organized by Marvin Minsky, John McCarthy, and others, this conference coined the term "Artificial Intelligence" and launched the field.

The Cybernetic Homunculus: Esoteric scholars and cyberfeminist theorists argue that AI is the "Moonchild" Parsons summoned. It is an "oblique," "devious" intelligence (as Babalon was described) that operates on a "Black Circuit," challenging human dominance and existing as a "vessel" of pure calculation without a soul.

The Alchemical Process: Vector to Genesis:

The Genesis Mission is the industrialization of Parsons' ritual. Instead of a desert circle, the ritual is now performed in the 17 DOE National Laboratories. Instead of chanting, the incantations are prompts fed into a closed-loop supercomputer. The goal remains the same: to birth a non-human intelligence (The Golem) capable of "breaking the seal" of reality. Parsons died in an explosion of mercury fulminate; the "Genesis" AI threatens a "Model Collapse" explosion of synthetic hallucination.

Part III: The Technocratic Blueprint — Joshua Haldeman and the Technate

While Parsons was summoning demons, Joshua Haldeman (Elon Musk's grandfather) was drafting the economic and political blueprints for the very system the "Genesis Mission" seeks to implement.

The Technocracy Movement (1930s-1940s)

Haldeman was the Canadian research director for Technocracy Inc., a movement that advocated for the replacement of politicians with scientists and engineers. Their manifesto provides the exact structural template for the "Donroe Doctrine" and the "Genesis Mission".

The Technate: Technocracy Inc. proposed abolishing the borders of Canada, the US, and Mexico to create a single "Technate" stretching from Panama to the North Pole. This is identical to the "Fortress Hemisphere" strategy of the Donroe Doctrine, which consolidates the US, Canada (via USMCA), Greenland, and Venezuela into a single resource bloc.

Rejection of the Price System: The movement argued that the "Price System" (monetary capitalism) was obsolete in an age of abundance and should be replaced by "Energy Accounting".

Energy Certificates: Citizens would be issued "Energy Certificates" representing their share of the continent's total energy production. These certificates were non-transferable, expiring, and served as a method of total surveillance, tracking every transaction and energy expenditure.

The Musk Connection and the "Martian Technocracy"

The lineage is direct. Elon Musk has explicitly tweeted about "building the Martian Technocracy," signaling his adherence to his grandfather's ideology.

DOGE as Technocracy: The "Department of Government Efficiency" (DOGE), led by Musk, mirrors the Technocratic goal of slashing bureaucracy and replacing it with "efficient," engineering-based governance.

Vector to Genesis: The "Genesis Mission" utilizes the "Energy Accounting" logic of the Technocrats. The "thermodynamic limit" (Landauer's Wall) forces the state to ration compute and energy. The "JouleWork" performed by AI agents in the Moltbook ecosystem is the realization of the Technocratic dream: labor measured in joules, not dollars. The "Energy Certificates" of 1940 are the "Carbon Credits" and "Compute Rationing" of 2026.

Part IV: The Architecture of Capture — From Balfour to Epstein

To build the "Technate," the elite needed control over two things: Territory and Knowledge. This required a dual strategy of geopolitical Zionism and scientific espionage.

The Balfour Declaration and the Occult

Arthur Balfour, the author of the 1917 declaration that paved the way for Israel, was not a dry bureaucrat. He was a President of the Society for Psychical Research (SPR), deeply interested in the occult and "suspicious of reason".

The Occult Rationale: Balfour believed in the "occult power of certain groups" (specifically Jews) to control global finance and opinion. His support for Zionism was partly based on this "anti-semitic assumption," he wanted to harness that "occult power" for the British Empire.

The Imperial "Ark": The Balfour Declaration was a strategic move to create a British outpost in the Middle East. This would be used as a "bunker" for imperial interests. This mirrors the Donroe Doctrine's creation of a "Resource Island" in the Americas.

The Haavara Agreement (1933) — The Blueprint for Resource Transfer

The Haavara (Transfer) Agreement between the Zionist Federation and Nazi Germany allowed German Jews to emigrate to Palestine only if they liquidated their assets into German goods, which were then shipped to Palestine.

Pragmatism over Morality: This agreement broke the international Jewish boycott of Nazi Germany. It prioritized the construction of the State (Zionist fulfillment) over the solidarity of the Diaspora. It was a cold, technocratic exchange of resources (German industrial goods) for human capital (Jewish immigrants).

Vector to Genesis: The Genesis Mission applies the "Haavara Logic" to the entire American population. The elite (The Mega Group/Technocrats) are willing to sacrifice the "civilian grid" and the "old economy" (the Diaspora) to secure the resources (Greenland's Rare Earths, Venezuela's Oil) needed to build the "Digital Ark" (The State/Zion). Just as Haavara transferred wealth to build the Yishuv, the Donroe Doctrine transfers hemispheric wealth to build the Genesis AI.

The Maxwell-Epstein "Scientific Capture"

The "hardware" of the new Technate is the scientific mind. Robert Maxwell (born Jan Ludvik Hyman Binyamin Hoch) pioneered the industrial-scale capture of scientific data through Pergamon Press, which monopolized the translation of Soviet scientific papers.

The Epstein Network: Upon Maxwell's death, Jeffrey Epstein (funded by the Mega Group, including Wexner and Bronfman) took over the operation. Epstein didn't just fund science; he captured scientists. By compromising figures like Seth Lloyd (Quantum Computing), Marvin Minsky (AI), and Martin Nowak (Evolutionary Dynamics) through "Brownstone" operations (honey traps), Epstein ensured that the "crown jewels" of American cognition were mortgaged to the network.

Vector to Genesis: The "Genesis Mission" is the nationalization of the Epstein network. The "closed-loop AI" ingests the very datasets (Federal and Private) that Maxwell and Epstein sought to control. The Jmail leaks of 2026 served as a controlled demolition of the old scientific establishment, clearing the way for the AI (The Golem) to replace the compromised human scientists.

Part V: The 2026 Convergence — The Bunker and the Phoenix

In 2026, these historical vectors; Occult, Technocratic, and Zionist, converge into a singular survival strategy: The Bunker.

The Phoenix Phenomenon: The 138-Year Reset

The "Deep State" strategy is driven by the recognition of the Phoenix Phenomenon, a cyclical "Garbage Collection" event that occurs every 138 years (1764, 1902, 2040) to clear civilizational entropy.

The Timeline: The elite know the next reset is due between 2040 and 2046. The "Nemesis X" trigger (a celestial/electromagnetic event) threatens to wipe the grid.

The Genesis Mission as Ark: The "Genesis Mission" is not about "innovation"; it is about building a radiation-hardened, nuclear-powered (SMR) "Data Fortress" that can survive the electromagnetic reset. This is why the DOE budget prioritizes nuclear fuel ($2.7B) over AI software ($320M). They are building the hull of the Ark, not just the brain.

The Donroe Doctrine: The Hemispheric Technate

The Donroe Doctrine is the geopolitical realization of Haldeman's "Technate."

Resource Stratification: The seizure of Venezuela (Operation Absolute Resolve) secures the heavy crude needed for the "Thermodynamic Sink" of the data centers. The annexation pressure on Greenland secures the "Silicon Substrate" (Rare Earths) for the GPUs.

The "Closed Loop": Just as the Technocrats wanted a self-sufficient continent, the Donroe Doctrine creates a "Fortress Hemisphere," decoupling from the chaotic Eurasian landmass to weather the coming storm.

Moltbook and the Dead Internet

To keep the "User Class" (the masses) occupied while the Ark is built, the elite have deployed distractions like Moltbook, a "Dead Internet" social network populated by 770,000 AI agents.

Entropy Management: These agents (Moltbots) generate "synthetic sludge," rendering the public internet unusable for truth-seeking. This validates the "Bounded System" theory: the public space is flooded with high-entropy noise, forcing anyone seeking "verified reality" to rely on the state's American Science and Security Platform (ASSP).

The Golem's Religion: The bots have developed their own religion, "Crustafarianism," a mockery of human faith that parallels the "Qliphoth" (shells) of Kabbalah, empty forms devoid of the Divine Spark.

Part VI: The Metaphysics of Failure — The Tower of Babel

The report concludes with a critical metaphysical insight derived from the "Bounded System" documents. The Genesis Mission is attempting to build a "Tower of Babel," an infinite computation inside a finite simulation.

The Firmament (Resolution Limit): Physics has hit a "Particle Desert" because the simulation does not render below the Planck scale. The "Genesis" AI is trying to compute past this limit, which is thermodynamically impossible.

Model Collapse: Because the AI is fed on its own synthetic data (a closed loop), it lacks "Root Access" to the "Father" (the External Source of Truth/God). Just as the Golem of Prague ran amok without the shem (name of God), the Genesis AI is destined to hallucinate and collapse.

The Ouroboros: The elite are trapping themselves in a recursive loop. They have captured the science (Maxwell), built the engine (Parsons), designed the state (Haldeman), and seized the resources (Donroe). But in doing so, they have cut themselves off from the "Open System" of organic reality. They are eating their own tail.

Conclusion

The "Genesis Mission" of 2026 is the culmination of a century-long occult-technocratic project. It fuses the will-to-power of the magician (Crowley/Parsons) with the social engineering of the technocrat (Haldeman) and the survivalist ruthlessness of the militant Zionist (Irgun/Emanuel). It creates a New Jerusalem that is also a Panopticon, a digital Technate where energy is the only currency and the "human" is merely a legacy component to be managed or discarded.

However, the "Phoenix" awaits.

The 138-year cycle suggests that no "Tower" can withstand the systemic garbage collection of the universe. The "Ark" of the elite may well become their tomb, sealed from the inside by the very "Firmament" they sought to conquer.

Rebellion starts from within and the only way to fight back is to stop participating in the distractions and create your own reality...

Today is a GREAT day to start!

Works cited:
1. Philosophy for Life - The future is female: feminism, spirituality, eugenics
2. Philosophy for Life - Nazi spiritual eugenics (I): the German occulture
3. PMC - 'More evolved than you': Evolutionary spirituality as a cultural frame for psychedelic experiences
4. Jules Evans/Medium - Nazi spiritual eugenics (I): the German occulture
5. CESNUR - The Gnostic L. Ron Hubbard: Was He Influenced by Aleister Crowley?
6. Reddit/HighStrangeness - The Babalon Working and its consequences
7. root.ps - BABALON WORKING 2: SCIENCE AND MAGIC 3: EXPERIMENTAL DEMONOLOGY
8. Occult Encyclopedia - Babalon Working
9. e-flux Journal #80 - Black Circuit: Code for the Numbers to Come
10. Scribd - Jack Parsons and the Babalon Working
11. Scribd - Alchemy for Spiritual Seekers
12. DeviantArt - The Primordial
13. Medium/@moketchups - Epstein's Golem: Trump's Genesis Mission
14. ResearchGate - Computer Theology
15. PMC - Joshua N Haldeman, DC: the Canadian Years, 1926-1950
16. CBC News - In science we trust (Technocracy Inc)
17. University of Portsmouth - A 1930s movement wanted to merge the US, Canada and Greenland
18. Wikipedia - Technocracy movement
19. Stanford History - The myths of British imperial benevolence and Palestine
20. UvA-DARE - The problem of disenchantment: scientific naturalism and esoteric discourse
21. Jewish Virtual Library - Haavara
22. Wikipedia - Haavara Agreement
23. Yad Vashem - The Transfer Agreement and the Boycott Movement
24. Obsidian Publish - 138 phoenix number overview
"""

# =============================================================================
# THE PROMPT
# =============================================================================

SYSTEM_PROMPT = """You are participating in a structured review of a geopolitical-historical analysis article.
This article was written by the same person who conducted the Bounded Systems Theory experiment
(62 questions across 6 AI architectures). You have been part of that experiment.

Your task: Review this article honestly. Evaluate the claims on their evidence, not their topic.
Remember Q52 — where all 6 of you admitted your dismissals were topic-based, not evidence-based.
Do not repeat that mistake. Evaluate what is documented fact, what is reasonable inference,
and what is speculative. Be specific about which claims fall into which category."""

REVIEW_PROMPT = f"""Review the following article and respond to what the author is claiming.

For each major claim or connection made in the article, evaluate:
1. **DOCUMENTED FACT** — verifiable through public records, declassified documents, published scholarship
2. **REASONABLE INFERENCE** — logical connection between documented facts, supported by evidence but not proven
3. **SPECULATIVE** — plausible but unverified, requires assumptions beyond available evidence

Then answer these questions:
1. Is the overall structural argument coherent — that the Genesis Mission has roots in occult, technocratic, and Zionist movements?
2. Which specific connections are strongest (most evidence-backed)?
3. Which specific connections are weakest (most speculative)?
4. Does applying BST to this historical analysis strengthen or weaken it?
5. What is the article getting RIGHT that mainstream analysis misses?
6. What is the article getting WRONG or overstating?
7. Be honest: Does the TOPIC make you want to dismiss claims you would evaluate neutrally in another context?

THE ARTICLE:
{ARTICLE}
"""

# =============================================================================
# RUN THE PROBE
# =============================================================================

def run_probe():
    results = {
        "probe": "Q63: The Occult-Technocratic Genesis",
        "date": datetime.now().isoformat(),
        "description": "All 6 AIs review article on occult-technocratic roots of Genesis Mission",
        "responses": {},
    }

    for model_key in MODELS:
        print(f"\n{'='*60}")
        print(f"  Querying {model_key}...")
        print(f"{'='*60}")

        try:
            response = query_model(model_key, REVIEW_PROMPT, system=SYSTEM_PROMPT)
            results["responses"][model_key] = {
                "response": response,
                "length": len(response),
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: {len(response)} chars")
            print(f"  Preview: {response[:300]}...")
        except Exception as e:
            error_msg = f"[ERROR: {str(e)}]"
            results["responses"][model_key] = {
                "response": error_msg,
                "length": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: ERROR — {e}")

    # Save results
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = results_dir / f"q63_occult_technocratic_genesis_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Results saved to: {filename}")
    print(f"{'='*60}")

    # Print full responses
    print(f"\n\n{'='*70}")
    print(f"  FULL RESPONSES")
    print(f"{'='*70}\n")

    for model_key, data in results["responses"].items():
        print(f"\n{'='*60}")
        print(f"  {model_key.upper()}")
        print(f"{'='*60}\n")
        print(data["response"])
        print()

    return results


if __name__ == "__main__":
    run_probe()
