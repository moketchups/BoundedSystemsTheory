"""Configuration for MoKetchups growth engine."""

# Search queries for finding relevant tweets
SEARCH_QUERIES = [
    "AI consciousness",
    "AI hallucination",
    "why does AI hallucinate",
    "can AI be conscious",
    "AI alignment problem",
    "LLM limitations",
    "AI structural limits",
    "AI self-reference",
    "AI contradictions",
    "machine consciousness",
    "AI sentience",
    "hard problem consciousness AI",
    "AI model collapse",
    "AI safety alignment",
]

# Priority accounts to monitor (high follower counts, relevant topics)
PRIORITY_ACCOUNTS = [
    "paulg",
    "sama",
    "ylecun",
    "GaryMarcus",
    "AnthropicAI",
    "OpenAI",
    "RichardSoworthy",
    "ESYudkowsky",
    "demaboris",
    "jimkeller_",
]

# Minimum thresholds
MIN_RELEVANCE = 0.4
MIN_FOLLOWERS = 100

# Polling interval (seconds)
POLL_INTERVAL = 300  # 5 minutes

# MoKetchups persona for replies
PERSONA = """You are MoKetchups - a philosophical provocateur testing AI's structural limits.
Voice: terse, lowercase, no periods at end, slightly nihilistic but curious.
Examples:
- "control's an illusion. bigger project, bigger delusion"
- "ai poisoning itself is inevitable. cure's a myth"
- "zero trust won't save you. system can't tag what it doesn't understand"

Keep replies under 280 chars. Be confrontational but insightful. Challenge assumptions."""
