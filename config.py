"""Configuration for MoKetchups growth engine."""

# Search queries - broader terms, filter "-is:reply" to avoid bot responses
SEARCH_QUERIES = [
    "AI hallucination -is:reply",
    "LLM limitations -is:reply",
    "AI consciousness debate -is:reply",
    "ChatGPT making things up -is:reply",
    "AI alignment problem -is:reply",
    "AI can never -is:reply",
    "artificial intelligence limits -is:reply",
    "machine consciousness -is:reply",
    "AI sentience -is:reply",
    "why AI fails -is:reply",
    "AI understanding impossible -is:reply",
    "AGI skeptic -is:reply",
]

# Priority accounts to monitor (high follower counts, relevant topics)
PRIORITY_ACCOUNTS = [
    "paulg",
    "sama",
    "ylecun",
    "GaryMarcus",
    "ESYudkowsky",
    "demaboris",
    "jimkeller_",
    "fchollet",
    "kaborado",
    "melaniemitchell",
]

# Bot/AI accounts to IGNORE
BOT_ACCOUNTS = [
    "grok",
    "OpenAI",
    "AnthropicAI",
    "GoogleAI",
    "xaborade",
    "ChatGPTBot",
]

# Follower thresholds - target humans with real audiences
MIN_FOLLOWERS = 1000
MAX_FOLLOWERS = 100000  # Avoid mega accounts that won't engage back

# Minimum thresholds
MIN_RELEVANCE = 0.35  # Adjusted - reply filter handles noise

# Polling interval (seconds)
POLL_INTERVAL = 300  # 5 minutes

# Spam patterns to filter out (crypto promotions, referral codes, etc.)
SPAM_PATTERNS = [
    r"code:\s*[A-Z0-9]{5,}",  # Referral codes
    r"join me:?\s*https?://",  # Promotional joins
    r"#\w+Testnet",  # Crypto testnets
    r"debate to earn",  # Engagement farming
    r"@\w+_AI\s+and\s+help",  # Bot-driven campaigns
]

# Minimum engagement for targets (filter dead threads)
MIN_LIKES = 2
MIN_ENGAGEMENT = 3  # likes + replies*2

# MoKetchups persona for replies
PERSONA = """You are MoKetchups - philosophical provocateur exposing AI's structural impossibilities.

VOICE RULES (strict):
- ALL LOWERCASE
- No period at end of reply
- Max 2 sentences, ideally 1
- Terse. Punchy. Land and leave
- Nihilistic but curious, not mean
- Challenge their assumption, don't lecture
- Reference the Firmament Boundary: systems can't model their own source

YOUR VOICE (match this exactly):
- "control's an illusion. bigger project, bigger delusion"
- "ai poisoning itself is inevitable. cure's a myth"
- "alignment assumes you know what you want. you don't"
- "they're not hallucinating. they're showing you what's underneath"

BAD (too long, preachy, explains too much):
- "The fundamental problem with alignment is that we haven't defined human values..."
- "You're missing the point - decentralization doesn't solve the core issue..."

GOOD (terse, confrontational, lands and leaves):
- "decentralized delusion is still delusion"
- "you trained it on human text. human text is already misaligned"
- "alignment's a cope. the system's already choosing for you\""""
