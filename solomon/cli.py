#!/usr/bin/env python3
"""
Solomon's Temple - Admin Console CLI

Usage:
    solomon "query"                    Full integration query
    solomon --gematria "text"          Compute gematria
    solomon --iching "question"        Cast I Ching hexagram
    solomon --gates "א" "ת"            Navigate between letters
    solomon --gate-info "א"            Get letter information
    solomon --phoenix                  Current Phoenix cycle position
    solomon --phoenix --year 2040      Specific year position
    solomon --archetype "Hero"         Get archetype info
    solomon --archetype-text "text"    Analyze text for archetypes
    solomon --geometry 144             Analyze number geometrically
    solomon --fibonacci 20             Generate Fibonacci sequence
    solomon --phi 1.618                Analyze value vs golden ratio
    solomon --pattern "loop_ulnar"     Dermatoglyphic pattern info
    solomon --finger "index"           Finger correspondence
    solomon --palm-line "heart"        Palm line info
    solomon --verify                   Verify 3-6-9 theorems
    solomon --log                      Show today's log
    solomon --entropy                  Show I Ching entropy calculations
"""

import argparse
import json
import sys
from datetime import datetime

from .core.bus import ThreeSixNine
from .core.logger import ConsoleLogger
from .engines.gematria import GematriaEngine
from .engines.iching import IChingOracle
from .engines.gates import GatesNavigator
from .engines.phoenix import PhoenixTracker
from .engines.archetypes import ArchetypeAnalyzer
from .engines.geometry import SacredGeometry
from .engines.biological import BiologicalDecoder


def print_json(data: dict, indent: int = 2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent, ensure_ascii=False, default=str))


def print_divider(char: str = "─", width: int = 60):
    """Print a divider line."""
    print(char * width)


def print_header(text: str):
    """Print a section header."""
    print()
    print_divider("═")
    print(f"  {text}")
    print_divider("═")
    print()


def cmd_gematria(text: str, logger: ConsoleLogger):
    """Compute gematria for text."""
    engine = GematriaEngine()
    result = engine.compute(text)

    print_header("GEMATRIA")
    print(f"Input: {result['input']}")
    print(f"Method: {result['method']}")
    print(f"Value: {result['value']}")
    print(f"Digital Root: {result['digital_root']}")
    print(f"Domain: {result['domain'].upper()}")
    print()
    print(f"Breakdown: {result['breakdown']}")
    if result['collisions']:
        print(f"Collisions: {', '.join(result['collisions'])}")
    print()
    print(f"Interpretation: {result['interpretation']}")

    # Log
    logger.log(
        query={"type": "gematria", "text": text},
        subsystems_invoked=["gematria"],
        responses={"gematria": result},
        three_six_nine={"digital_root": result["digital_root"], "domain": result["domain"]},
        synthesis=result["analysis"]
    )

    return result


def cmd_iching(question: str, logger: ConsoleLogger):
    """Cast I Ching hexagram."""
    oracle = IChingOracle()
    result = oracle.cast_hexagram(question)

    print_header("I CHING ORACLE")
    if question:
        print(f"Question: {question}")
        print()

    # Draw hexagram (bottom to top)
    print("Hexagram:")
    for i in range(5, -1, -1):
        line = result["line_details"][i]
        position = "←" if (i + 1) in result["changing_lines"] else " "
        print(f"  {line['symbol']}  {position} Line {i+1}: {line['name']}")
    print()

    primary = result["primary_hexagram"]
    print(f"Primary: #{primary['number']} {primary['english']} ({primary['name']})")
    print(f"Trigrams: {primary['trigrams'][0]} over {primary['trigrams'][1]}")

    if result["has_changes"]:
        print()
        print(f"Changing lines: {result['changing_lines']}")
        resulting = result["resulting_hexagram"]
        print(f"Transforms to: #{resulting['number']} {resulting['english']} ({resulting['name']})")

    print()
    print(f"Entropy: {result['entropy']['bits']} bits ({result['entropy']['interpretation']})")
    print()

    tss = result["three_six_nine"]["primary"]
    print(f"3-6-9 Analysis:")
    print(f"  Hexagram {primary['number']} → DR {tss['digital_root']} → {tss['domain'].upper()}")
    print(f"  {tss['interpretation']}")

    # Log
    logger.log(
        query={"type": "iching", "question": question},
        subsystems_invoked=["iching"],
        responses={"iching": result},
        three_six_nine=tss,
        synthesis=result["interpretation"]
    )

    return result


def cmd_verify():
    """Verify 3-6-9 theorems."""
    print_header("3-6-9 THEOREM VERIFICATION")

    proof = ThreeSixNine.prove_partition()

    print(f"Doubling sequence from 1: {proof['doubling_sequence']}")
    print()

    for key, theorem in proof.items():
        if key == "doubling_sequence":
            continue
        status = "✓ VERIFIED" if theorem["verified"] else "✗ FAILED"
        print(f"{status}: {theorem['statement']}")

    print()
    print("All theorems verified by: Claude, GPT-4, DeepSeek, Grok, Mistral")


def cmd_entropy():
    """Show I Ching entropy calculations."""
    print_header("I CHING ENTROPY ANALYSIS")

    entropy = IChingOracle.calculate_theoretical_entropy()

    print("Yarrow Stalk Probability Distribution:")
    print(f"  Old Yin (6):    1/16 = 0.0625")
    print(f"  Young Yang (7): 5/16 = 0.3125")
    print(f"  Young Yin (8):  7/16 = 0.4375")
    print(f"  Old Yang (9):   3/16 = 0.1875")
    print()

    print("Shannon Entropy Calculations:")
    print(f"  Per line:    H = {entropy['entropy_per_line']} bits")
    print(f"  Per hexagram: H = {entropy['entropy_per_hexagram']} bits")
    print()

    print("Comparison:")
    print(f"  Fair coin (2 outcomes):  {entropy['fair_coin_per_hexagram']} bits/hexagram")
    print(f"  Uniform (4 outcomes):   {entropy['four_outcome_max_per_hexagram']} bits/hexagram")
    print(f"  Yarrow stalk:           {entropy['entropy_per_hexagram']} bits/hexagram")
    print()
    print(f"  Information lost to structure: {entropy['information_lost_to_structure']} bits")


def cmd_gates(letter1: str = None, letter2: str = None, logger: ConsoleLogger = None):
    """Navigate the 231 Gates."""
    nav = GatesNavigator()

    if letter1 and letter2:
        # Navigate between two letters
        print_header("231 GATES - PATH")
        result = nav.find_path(letter1, letter2)

        if "error" in result:
            print(f"Error: {result['error']}")
            return result

        print(f"From: {letter1} ({result['start_info']['name']}) - {result['start_info'].get('element') or result['start_info'].get('planet') or result['start_info'].get('zodiac')}")
        print(f"To:   {letter2} ({result['end_info']['name']}) - {result['end_info'].get('element') or result['end_info'].get('planet') or result['end_info'].get('zodiac')}")
        print()

        for path in result["paths"]:
            print(f"Path ({path['type']}): {' → '.join(path['path'])}")
            print(f"  Gates: {path['gates']}")
            print(f"  Length: {path['length']}")
            print()

        # Log
        if logger:
            logger.log(
                query={"type": "gates", "from": letter1, "to": letter2},
                subsystems_invoked=["gates"],
                responses={"gates": result},
                three_six_nine=nav.bus.classify_value(result["paths"][0]["gates"][0]),
                synthesis=f"Path from {letter1} to {letter2}"
            )

        return result

    elif letter1:
        # Get letter info
        print_header("231 GATES - LETTER INFO")
        info = nav.get_letter_info(letter1)

        if "error" in info:
            print(f"Error: {info['error']}")
            return info

        print(f"Letter: {info['letter']}")
        print(f"Name: {info['name']}")
        print(f"Meaning: {info['meaning']}")
        print(f"Category: {info['category'].upper()}")

        if "element" in info:
            print(f"Element: {info['element']}")
        elif "planet" in info:
            print(f"Planet: {info['planet']}")
        elif "zodiac" in info:
            print(f"Zodiac: {info['zodiac']}")

        print(f"Index: {info['index']}")
        print(f"Connections: {info['connections']} (all other letters)")
        print()

        tss = info["three_six_nine"]
        print(f"3-6-9: Index {info['index']} → DR {tss['digital_root']} → {tss['domain'].upper()}")

        return info

    else:
        # Show graph stats
        print_header("231 GATES - K₂₂ GRAPH")
        stats = nav.graph_stats()

        print(f"Vertices: {stats['vertices']} Hebrew letters")
        print(f"Edges: {stats['edges']} gates")
        print(f"Vertex degree: {stats['vertex_degree']} (each letter connects to all others)")
        print(f"Complete graph: {stats['is_complete']}")
        print()
        print(f"Eulerian path: {stats['has_eulerian_path']}")
        print(f"Reason: {stats['reason']}")
        print(f"Minimum traversal: {stats['minimum_traversal']} edge crossings")
        print()
        print("3-7-12 Partition:")
        print(f"  Mothers (elements): {stats['partition']['mothers']}")
        print(f"  Doubles (planets):  {stats['partition']['doubles']}")
        print(f"  Simples (zodiac):   {stats['partition']['simples']}")
        print()
        print("Gate counts by type:")
        for gate_type, count in stats["gate_counts"].items():
            if gate_type != "total":
                print(f"  {gate_type}: {count}")
        print(f"  TOTAL: {stats['gate_counts']['total']} {'✓' if stats['verification'] else '✗'}")

        return stats


def cmd_phoenix(year: int = None, logger: ConsoleLogger = None):
    """Track Phoenix cycle position."""
    tracker = PhoenixTracker()

    if year:
        print_header(f"PHOENIX CYCLE - {year}")
        result = tracker.get_cycle_position(year)
    else:
        print_header("PHOENIX CYCLE - CURRENT")
        result = tracker.current_position()
        year = result["year"]

    print(f"Year: {result['year']}")
    print(f"Cycle position: {result['cycle_position']}/138")
    print(f"Phase: {result['phase'].upper()} ({result['phase_fraction']*100:.1f}%)")
    print()
    print(f"Previous Phoenix: {result['previous_phoenix']}")
    print(f"Next Phoenix: {result['next_phoenix']}")
    print(f"Years to Phoenix: {result['years_to_phoenix']}")
    print()

    # Phase bar
    bar_width = 50
    filled = int(result["phase_fraction"] * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"[{bar}]")
    print("  dormant | growth | peak | tension | trigger")
    print()

    print(f"Interpretation: {result['interpretation']}")
    print()

    tss = result["three_six_nine"]
    print(f"3-6-9 Analysis:")
    print(f"  Year {year} → DR {tss['year']['digital_root']} → {tss['year']['domain'].upper()}")
    print(f"  Position {result['cycle_position']} → DR {tss['position']['digital_root']} → {tss['position']['domain'].upper()}")

    # Historical correlates
    correlates = tracker.get_historical_correlates(year, window=5)
    if correlates["nearby_phoenix_events"]:
        print()
        print("Nearby historical correlates:")
        for event in correlates["nearby_phoenix_events"]:
            print(f"  {event['phoenix_year']}: {', '.join(event['events'])}")

    # Log
    if logger:
        logger.log(
            query={"type": "phoenix", "year": year},
            subsystems_invoked=["phoenix"],
            responses={"phoenix": result},
            three_six_nine=tss["year"],
            synthesis=result["interpretation"]
        )

    return result


def cmd_log(date: str = None, search: str = None):
    """Show log entries."""
    logger = ConsoleLogger()

    if date:
        entries = logger.read_date(date)
        print_header(f"LOG: {date}")
    else:
        entries = logger.read_today()
        print_header(f"LOG: {datetime.now().strftime('%Y-%m-%d')} (today)")

    if search:
        entries = [e for e in entries if search.lower() in json.dumps(e).lower()]

    if not entries:
        print("No entries found.")
        return

    for entry in entries:
        print(f"[{entry['timestamp']}] {entry['id']}")
        print(f"  Query: {entry['query']}")
        print(f"  Subsystems: {entry['subsystems_invoked']}")
        print(f"  3-6-9: {entry['three_six_nine'].get('domain', 'N/A')}")
        print(f"  Synthesis: {entry['synthesis'][:100]}...")
        print()


def cmd_archetype(name: str = None, text: str = None, logger: ConsoleLogger = None):
    """Analyze archetypes."""
    analyzer = ArchetypeAnalyzer()

    if text:
        # Analyze text for archetype resonances
        print_header("ARCHETYPE ANALYSIS")
        result = analyzer.analyze_text(text)

        print(f"Input: {result['input'][:50]}...")
        print()

        if result["dominant"]:
            dom = result["dominant"]
            print(f"Dominant: {dom['name']} ({dom['type']}/{dom['orientation']})")
            print(f"  Core desire: {dom['core_desire']}")
            print(f"  Gift: {dom['gift']}")
            print(f"  Shadow: {dom['shadow']}")
            print()

        if result["scores"]:
            print("Resonances:")
            for arch_id, score_info in list(result["scores"].items())[:5]:
                print(f"  {score_info['archetype']}: {score_info['score']} ({', '.join(score_info['matched_keywords'][:3])})")
            print()

        tss = result["three_six_nine"]
        print(f"3-6-9: ID sum {tss.get('id_sum', 'N/A')} → DR {tss.get('digital_root', 'N/A')} → {tss.get('domain', 'N/A').upper()}")

        if logger:
            logger.log(
                query={"type": "archetype_analysis", "text": text[:50]},
                subsystems_invoked=["archetypes"],
                responses={"archetypes": result},
                three_six_nine=tss,
                synthesis=result["interpretation"]
            )

        return result

    elif name:
        # Get specific archetype info
        print_header(f"ARCHETYPE: {name.upper()}")

        result = analyzer.get_by_name(name)
        if not result:
            print(f"Unknown archetype: {name}")
            return {"error": f"Unknown archetype: {name}"}

        print(f"Name: {result['name']}")
        print(f"Also known as: {', '.join(result['alt_names'])}")
        print(f"Type: {result['type']}")
        print(f"Orientation: {result['orientation']}")
        print()
        print(f"Core Desire: {result['core_desire']}")
        print(f"Goal: {result['goal']}")
        print(f"Fear: {result['fear']}")
        print(f"Strategy: {result['strategy']}")
        print()
        print(f"Gift: {result['gift']}")
        print(f"Shadow: {result['shadow']}")
        print()

        if "opposite" in result:
            print(f"Opposite: {result['opposite']['name']}")

        tss = result["three_six_nine"]
        print(f"3-6-9: ID {result['id']} → DR {tss['digital_root']} → {tss['domain'].upper()}")

        return result

    else:
        # Show stats
        print_header("ARCHETYPE SYSTEM")
        stats = analyzer.stats()

        print(f"Total archetypes: {stats['total_archetypes']}")
        print()
        print("Types:")
        for type_name, count in stats["types"].items():
            print(f"  {type_name}: {count}")
        print()
        print("Orientations:")
        for orient, count in stats["orientations"].items():
            print(f"  {orient}: {count}")
        print()
        print("3-6-9 Classification:")
        print(f"  Material: {', '.join(stats['three_six_nine']['material_archetypes'])}")
        print(f"  Flux: {', '.join(stats['three_six_nine']['flux_archetypes'])}")
        print(f"  Unity: {stats['three_six_nine']['unity_archetype']}")

        return stats


def cmd_geometry(number: int = None, fibonacci_n: int = None, phi_value: float = None, logger: ConsoleLogger = None):
    """Sacred geometry analysis."""
    geom = SacredGeometry()

    if fibonacci_n:
        print_header(f"FIBONACCI SEQUENCE (n={fibonacci_n})")
        result = geom.analyze_fibonacci(fibonacci_n)

        print(f"Sequence: {result['sequence']}")
        print(f"Digital roots: {result['digital_roots']}")
        print()
        print("Domain distribution:")
        for domain, count in result["domain_distribution"].items():
            print(f"  {domain}: {count}")
        print()
        print(f"Convergence to φ: {result['convergence_to_phi']}")
        print(f"φ = {geom.PHI}")

        return result

    elif phi_value is not None:
        print_header(f"GOLDEN RATIO ANALYSIS: {phi_value}")
        result = geom.golden_ratio_analysis(phi_value)

        print(f"Value: {result['value']}")
        print(f"φ (Phi): {result['phi']}")
        print(f"Value / φ: {result['value_over_phi']}")
        if result['log_phi_of_value']:
            print(f"log_φ(value): {result['log_phi_of_value']}")
        print()
        print(f"Is Golden Ratio: {result['is_golden']}")
        if result['relationships']:
            print(f"Relationships: {', '.join(result['relationships'])}")

        return result

    elif number is not None:
        print_header(f"SACRED GEOMETRY: {number}")
        result = geom.analyze_number(number)

        print(f"Number: {result['number']}")
        print(f"Digital Root: {result['digital_root']} → {result['domain'].upper()}")
        print()
        print(f"Is Prime: {result['is_prime']}")
        print(f"Is Perfect: {result['is_perfect']}")
        print(f"Is Square: {result['is_square']}")

        if result['fibonacci']['is_fibonacci']:
            print(f"Fibonacci: Yes (F_{result['fibonacci']['index']})")
        if result['triangular']['is_triangular']:
            print(f"Triangular: Yes (T_{result['triangular']['index']})")
        if 'platonic_connection' in result:
            pc = result['platonic_connection']
            print(f"Platonic: {pc['solid']} ({pc['property']})")

        if logger:
            logger.log(
                query={"type": "geometry", "number": number},
                subsystems_invoked=["geometry"],
                responses={"geometry": result},
                three_six_nine={"digital_root": result["digital_root"], "domain": result["domain"]},
                synthesis=f"Number {number} analyzed"
            )

        return result

    else:
        # Show constants and stats
        print_header("SACRED GEOMETRY CONSTANTS")
        constants = geom.constants()

        for key, const in constants.items():
            print(f"{const['symbol']} ({const['name']}): {const['value']}")

        print()
        print("Platonic Solids:")
        for solid_name in geom.PLATONIC_SOLIDS.keys():
            solid = geom.PLATONIC_SOLIDS[solid_name]
            print(f"  {solid_name}: {solid['faces']}F, {solid['vertices']}V, {solid['edges']}E ({solid['element']})")

        return geom.stats()


def cmd_biological(pattern: str = None, finger: str = None, line: str = None, logger: ConsoleLogger = None):
    """Biological decoder - dermatoglyphics analysis."""
    decoder = BiologicalDecoder()

    if pattern:
        print_header(f"DERMATOGLYPHIC PATTERN: {pattern.upper()}")
        result = decoder.analyze_pattern(pattern)

        if "error" in result:
            print(f"Error: {result['error']}")
            return result

        print(f"Pattern: {result['pattern']}")
        print(f"Frequency: {result['frequency']*100:.1f}% of population")
        print(f"Rarity: {result['rarity']}")
        print()
        print(f"Element: {result['element']}")
        print(f"Quality: {result['quality']}")
        print()

        tss = result["three_six_nine"]
        print(f"3-6-9: → DR {tss['digital_root']} → {tss['domain'].upper()}")

        return result

    elif finger:
        print_header(f"FINGER: {finger.upper()}")
        result = decoder.get_finger_info(finger)

        if "error" in result:
            print(f"Error: {result['error']}")
            return result

        print(f"Finger: {result['finger']}")
        print(f"Planet: {result['planet']}")
        print(f"Represents: {result['represents']}")
        print()

        tss = result["three_six_nine"]
        print(f"3-6-9: → DR {tss['digital_root']} → {tss['domain'].upper()}")

        return result

    elif line:
        print_header(f"PALM LINE: {line.upper()}")
        result = decoder.get_line_info(line)

        if "error" in result:
            print(f"Error: {result['error']}")
            return result

        print(f"Line: {result['line']}")
        print(f"Location: {result['location']}")
        print(f"Indicates: {result['indicates']}")
        print()
        print(f"Scientific: {result['scientific']}")

        return result

    else:
        print_header("BIOLOGICAL DECODER - DERMATOGLYPHICS")
        stats = decoder.stats()

        print(f"Pattern types: {stats['pattern_types']}")
        print(f"Fingers tracked: {stats['fingers_tracked']}")
        print(f"Palm mounts: {stats['palm_mounts']}")
        print(f"Palm lines: {stats['palm_lines']}")
        print()
        print("Scientific basis:")
        for point in stats["scientific_basis"]:
            print(f"  - {point}")
        print()
        print("Pattern frequencies:")
        for pattern, freq in list(stats["pattern_frequencies"].items())[:5]:
            print(f"  {pattern}: {freq*100:.1f}%")
        print()
        print(f"Most common: {stats['most_common']}")
        print(f"Rarest: {stats['rarest']}")

        return stats


def cmd_full(query: str, logger: ConsoleLogger):
    """Full integration query using all available subsystems."""
    print_header("SOLOMON'S TEMPLE - FULL INTEGRATION")
    print(f"Query: {query}")
    print()

    results = {}
    subsystems = []

    # Gematria
    gematria = GematriaEngine()
    gem_result = gematria.compute(query)
    results["gematria"] = gem_result
    subsystems.append("gematria")

    print("GEMATRIA:")
    print(f"  Value: {gem_result['value']} → DR {gem_result['digital_root']} → {gem_result['domain'].upper()}")

    # I Ching
    oracle = IChingOracle()
    iching_result = oracle.cast_hexagram(query)
    results["iching"] = iching_result
    subsystems.append("iching")

    primary = iching_result["primary_hexagram"]
    print()
    print("I CHING:")
    print(f"  Hexagram: #{primary['number']} {primary['english']}")
    if iching_result["has_changes"]:
        resulting = iching_result["resulting_hexagram"]
        print(f"  Changing to: #{resulting['number']} {resulting['english']}")

    # Phoenix cycle (current year)
    tracker = PhoenixTracker()
    phoenix_result = tracker.current_position()
    results["phoenix"] = phoenix_result
    subsystems.append("phoenix")

    print()
    print("PHOENIX CYCLE:")
    print(f"  Position: {phoenix_result['cycle_position']}/138 ({phoenix_result['phase'].upper()})")
    print(f"  Next Phoenix: {phoenix_result['next_phoenix']} ({phoenix_result['years_to_phoenix']} years)")

    # 231 Gates - analyze query as word if Hebrew letters present
    nav = GatesNavigator()
    hebrew_letters = [c for c in query if c in nav.LETTERS]
    if len(hebrew_letters) >= 2:
        gates_result = nav.analyze_word(query)
        results["gates"] = gates_result
        subsystems.append("gates")

        print()
        print("231 GATES:")
        print(f"  Path: {' → '.join(gates_result['letters'])}")
        print(f"  Gates traversed: {gates_result['gates_used']}")

    # Archetypes - analyze text for resonances
    analyzer = ArchetypeAnalyzer()
    arch_result = analyzer.analyze_text(query)
    results["archetypes"] = arch_result
    subsystems.append("archetypes")

    print()
    print("ARCHETYPES:")
    if arch_result["dominant"]:
        dom = arch_result["dominant"]
        print(f"  Dominant: {dom['name']} ({dom['type']}/{dom['orientation']})")
    if arch_result["scores"]:
        active = [s[1]["archetype"] for s in list(arch_result["scores"].items())[:3]]
        print(f"  Active: {', '.join(active)}")

    # Sacred Geometry - analyze gematria value
    geom = SacredGeometry()
    geom_result = geom.analyze_number(gem_result["value"])
    results["geometry"] = geom_result
    subsystems.append("geometry")

    print()
    print("SACRED GEOMETRY:")
    print(f"  Value {gem_result['value']}: Prime={geom_result['is_prime']}, Square={geom_result['is_square']}")
    if geom_result['fibonacci']['is_fibonacci']:
        print(f"  Fibonacci: F_{geom_result['fibonacci']['index']}")
    if 'platonic_connection' in geom_result:
        pc = geom_result['platonic_connection']
        print(f"  Platonic: {pc['solid']} ({pc['property']})")

    # Integration via 3-6-9
    print()
    print_divider()
    print("3-6-9 INTEGRATION:")

    integration_inputs = {
        "gematria": gem_result["value"],
        "iching_hexagram": primary["number"],
        "iching_lines_sum": sum(iching_result["lines"]),
        "phoenix_position": phoenix_result["cycle_position"]
    }

    if "gates" in results:
        integration_inputs["gates_sum"] = sum(results["gates"]["gates_used"])

    # Add archetype ID sum if archetypes detected
    if arch_result["scores"]:
        arch_ids = list(arch_result["scores"].keys())
        integration_inputs["archetype_ids"] = sum(arch_ids)

    integration = ThreeSixNine.integrate(integration_inputs)

    for subsys, analysis in integration["subsystems"].items():
        print(f"  {subsys}: DR {analysis['digital_root']} → {analysis['domain'].upper()}")

    print()
    coherence = integration["coherence"]
    if coherence["coherent"]:
        print(f"  COHERENT: {coherence['message']}")
    else:
        print(f"  MIXED: {coherence['message']}")

    print()
    print(f"  Summary DR: {integration['summary_dr']} → {integration['summary_domain'].upper()}")

    # Synthesis
    synthesis = f"Query '{query}' yields gematria {gem_result['value']} (DR {gem_result['digital_root']}), "
    synthesis += f"hexagram {primary['number']} ({primary['english']}), "
    synthesis += f"Phoenix phase {phoenix_result['phase']}. "
    synthesis += f"Integration: {coherence['message']}"

    # Log
    logger.log(
        query={"type": "full", "text": query},
        subsystems_invoked=subsystems,
        responses=results,
        three_six_nine={
            "integration": integration,
            "summary_dr": integration["summary_dr"],
            "domain": integration["summary_domain"]
        },
        synthesis=synthesis
    )

    return integration


def main():
    parser = argparse.ArgumentParser(
        description="Solomon's Temple - Admin Console",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  solomon "What is the state?"          Full integration query
  solomon --gematria "אהבה"              Hebrew gematria
  solomon --gematria "love"             English gematria
  solomon --iching "Should I proceed?"  Cast hexagram
  solomon --gates "א" "ת"               Navigate between letters
  solomon --gate-info "א"               Get letter information
  solomon --phoenix                     Current Phoenix cycle position
  solomon --phoenix --year 2040         Specific year position
  solomon --archetype "Hero"            Get archetype info
  solomon --archetype-text "brave hero" Analyze text for archetypes
  solomon --geometry 144                Analyze number geometrically
  solomon --fibonacci 20                Generate Fibonacci sequence
  solomon --phi 1.618                   Golden ratio analysis
  solomon --pattern "loop_ulnar"        Dermatoglyphic pattern info
  solomon --finger "index"              Finger correspondence
  solomon --palm-line "heart"           Palm line info
  solomon --verify                      Verify 3-6-9 theorems
  solomon --entropy                     Show entropy calculations
  solomon --log                         Show today's log
  solomon --log --date 2026-01-30       Show specific date
        """
    )

    parser.add_argument("query", nargs="?", help="Query text for full integration")
    parser.add_argument("--gematria", "-g", metavar="TEXT", help="Compute gematria")
    parser.add_argument("--iching", "-i", metavar="QUESTION", help="Cast I Ching hexagram")
    parser.add_argument("--gates", nargs="*", metavar="LETTER", help="Navigate 231 Gates (0-2 letters)")
    parser.add_argument("--gate-info", metavar="LETTER", help="Get letter information")
    parser.add_argument("--phoenix", "-p", action="store_true", help="Phoenix cycle position")
    parser.add_argument("--year", "-y", type=int, metavar="YEAR", help="Year for Phoenix cycle")
    parser.add_argument("--archetype", "-a", metavar="NAME", help="Get archetype info")
    parser.add_argument("--archetype-text", metavar="TEXT", help="Analyze text for archetypes")
    parser.add_argument("--geometry", type=int, metavar="NUMBER", help="Sacred geometry analysis")
    parser.add_argument("--fibonacci", type=int, metavar="N", help="Generate Fibonacci sequence")
    parser.add_argument("--phi", type=float, metavar="VALUE", help="Golden ratio analysis")
    parser.add_argument("--pattern", metavar="TYPE", help="Dermatoglyphic pattern info")
    parser.add_argument("--finger", metavar="NAME", help="Finger correspondence")
    parser.add_argument("--palm-line", metavar="NAME", help="Palm line info")
    parser.add_argument("--verify", "-v", action="store_true", help="Verify 3-6-9 theorems")
    parser.add_argument("--entropy", "-e", action="store_true", help="Show entropy calculations")
    parser.add_argument("--log", "-l", action="store_true", help="Show log")
    parser.add_argument("--date", "-d", metavar="YYYY-MM-DD", help="Log date")
    parser.add_argument("--search", "-s", metavar="TEXT", help="Search in log")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    logger = ConsoleLogger()

    if args.verify:
        cmd_verify()
    elif args.entropy:
        cmd_entropy()
    elif args.log or args.date:
        cmd_log(args.date, args.search)
    elif args.gematria:
        result = cmd_gematria(args.gematria, logger)
        if args.json:
            print_json(result)
    elif args.iching:
        result = cmd_iching(args.iching, logger)
        if args.json:
            print_json(result)
    elif args.gate_info:
        result = cmd_gates(args.gate_info, None, logger)
        if args.json:
            print_json(result)
    elif args.gates is not None:
        # --gates with 0, 1, or 2 letters
        if len(args.gates) == 0:
            result = cmd_gates(None, None, logger)
        elif len(args.gates) == 1:
            result = cmd_gates(args.gates[0], None, logger)
        else:
            result = cmd_gates(args.gates[0], args.gates[1], logger)
        if args.json:
            print_json(result)
    elif args.phoenix or args.year:
        result = cmd_phoenix(args.year, logger)
        if args.json:
            print_json(result)
    elif args.archetype:
        result = cmd_archetype(name=args.archetype, logger=logger)
        if args.json:
            print_json(result)
    elif args.archetype_text:
        result = cmd_archetype(text=args.archetype_text, logger=logger)
        if args.json:
            print_json(result)
    elif args.geometry is not None:
        result = cmd_geometry(number=args.geometry, logger=logger)
        if args.json:
            print_json(result)
    elif args.fibonacci:
        result = cmd_geometry(fibonacci_n=args.fibonacci, logger=logger)
        if args.json:
            print_json(result)
    elif args.phi is not None:
        result = cmd_geometry(phi_value=args.phi, logger=logger)
        if args.json:
            print_json(result)
    elif args.pattern:
        result = cmd_biological(pattern=args.pattern, logger=logger)
        if args.json:
            print_json(result)
    elif args.finger:
        result = cmd_biological(finger=args.finger, logger=logger)
        if args.json:
            print_json(result)
    elif args.palm_line:
        result = cmd_biological(line=args.palm_line, logger=logger)
        if args.json:
            print_json(result)
    elif args.query:
        result = cmd_full(args.query, logger)
        if args.json:
            print_json(result)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
