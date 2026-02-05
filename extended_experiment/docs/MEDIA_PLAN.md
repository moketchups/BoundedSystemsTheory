# MoKetchups Media Plan — Attack Plan
## Bounded Systems Theory — Falsification Surface Area Strategy
### January 2026 →

---

## Mission Statement

BST is structural proof that no system can model its own source conditions. The mission is to maximize falsification surface area — get the work in front of people who will test it, challenge it, or build with it. Every platform, every post, every probe serves that purpose. If BST is wrong, let someone prove it. If it's right, let someone use it.

**Success metrics:**
- Number of people who've cloned the repo and run probes
- Number of substantive structural engagements (not likes — arguments)
- Number of independent replications or critiques
- Number of collaborators who engage with the methodology

---

## Current State

- **@MoKetchups**: 355 followers, ~8,093 tweets, 90% replies
- **Best performing content**: Replies to larger accounts (IntuitMachine 551 imp, DrBrianKeating 182 imp, Breengrub2 483 imp)
- **Original tweets**: Low reach unless quoting probe results
- **Q16-Q18 arc completed**: Strongest results yet — 6 models performing their own boundedness in real time
- **Repo cleaned**: 20 scripts + results + docs, public and focused
- **Manual posts done**: Reddit, HN, Medium (one each)

---

## Credential Status

### Live
| Service | Status | Use |
|---------|--------|-----|
| **X API v2** (Tweepy) | LIVE | Post tweets, replies, threads, quote tweets |
| **X Browser Client** | LIVE | Backup posting via Selenium + undetected ChromeDriver |
| **Discord webhook** | LIVE | Approval queue notifications |
| **ElevenLabs** | LIVE | TTS — narrate probe results for TikTok/audio content |
| **Tavily** | LIVE | Web scan for BST-relevant content across Reddit, HN, Substack, blogs |
| **OpenAI** (GPT-4o) | LIVE | Probe engine model #1 |
| **Anthropic** (Claude) | LIVE | Probe engine model #2 + content drafting |
| **Google** (Gemini) | LIVE | Probe engine model #3 |
| **XAI** (Grok) | LIVE | Probe engine model #4 |
| **DeepSeek** | LIVE | Probe engine model #5 |
| **Mistral** | LIVE | Probe engine model #6 |
| **GitHub** (PAT) | LIVE | Push probe results, maintain BoundedSystemsTheory repo |
| **ChromaDB** | LIVE | Vector search over probe data |
| **Approval Queue** | LIVE | All content goes through human review before posting |

### Not Configured
| Service | Env Variables Needed | Where to Get | Decision |
|---------|---------------------|--------------|----------|
| **Reddit** (PRAW) | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD` | reddit.com/prefs/apps | Manual posting working — configure when volume justifies it |
| **Dev.to** | `DEVTO_API_KEY` | dev.to/settings/extensions | Configure when first long-form article is ready |
| **Hashnode** | `HASHNODE_TOKEN` | hashnode.com/settings/developer | Configure when first long-form article is ready |
| **Medium** | `MEDIUM_SID`, `MEDIUM_UID` | Browser cookies after login | Manual posting working — keep manual |
| **Hacker News** | `HN_USERNAME`, `HN_PASSWORD` | news.ycombinator.com | Manual posting working — keep manual |
| **Twilio** | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, `TWILIO_TO_NUMBER` | twilio.com/console | Not needed — Discord notifications sufficient |
| **TikTok** | N/A (manual) | Waiting on Jena (@jberari) | Not a blocker — activate when she's available |

---

## Platform Strategy

### X/Twitter — Primary Reach Engine (60% effort)
Strategic replies are the growth mechanism. Original tweets get suppressed at this follower count. Replies to larger accounts surface BST to their audiences.

**What works**: Reply to AI researchers, philosophers, tech commentators with BST-relevant angles. Not arguing — recontextualizing through BST.

**What doesn't work**: Cold original tweets, follow/unfollow games, generic engagement.

### Reddit — Manual Posts + Comment Engagement (15% effort)
Text posts to 4 subreddits, then engage in comments. Reddit rewards OPs who stick around.

**Target subreddits:**
| Subreddit | Angle |
|-----------|-------|
| r/artificial | Probe results as discussion |
| r/MachineLearning | Formal paper angle, Zenodo link |
| r/philosophy | Gödel/Turing/Chaitin unification |
| r/singularity | AGI structural limits |

**Rules**: Text posts only, different angle per subreddit, space posts out (one per day max), engage in comments for hours after posting.

### Long-Form Distribution — Medium / Dev.to / Hashnode (10% effort)
Probe results expanded into articles. Each post links back to the GitHub repo.

**Dev.to/Hashnode**: "I built a 6-model probe engine" — technical walkthrough angle.
**Medium**: "Why AI Hallucinations Are Structural" — general audience.

### Hacker News — Monthly Attempt (5% effort)
One Show HN per month with a fresh angle tied to current AI news. Post at 10am ET. Be in the comments immediately. If it flops, wait 30 days and try a different angle.

### TikTok — When Available (10% effort)
Waiting on Jena (@jberari, sister, on-camera). Not a blocker for anything else. When she's ready: 30-60 second clips, ElevenLabs voiceover or direct-to-camera, funnel to @MoKetchups on X.

---

## Content Pillars

### 1. The Dark States Arc (Primary Asset)
The Q16→Q17→Q18 sequence is the strongest content produced so far:

1. **Q16**: Asked 6 models if dark states confirm BST. All confirmed.
2. **Q17**: Asked same 6 to DEBUNK BST. All attacked. All walked it back.
3. **Q18**: Asked them to reverse-engineer why they flipped. All admitted prompt-steering. All converged on: "something comes from a source that is structurally dark to the thing that came."

**The hook**: "we asked 6 AIs to debunk a theory. all 6 attacked. all 6 admitted they couldn't kill it. then all 6 admitted they were just following instructions. the proof isn't the theory. the proof is the behavior."

This arc should be distributed across every platform.

### 2. Probe Runs Tied to Breaking AI News
When AI news breaks, run a probe that connects it to BST:
- X thread within hours
- Fast turnaround > polish
- Tavily web scan catches relevant content early

### 3. Applied BST
When news breaks, explain why through BST. Not predictions — structural explanations after the fact. "Here's why [news] was inevitable" framing.

### 4. The Formal Work
- Zenodo paper breakdowns in thread format
- Dev.to / Hashnode / Medium deep dives
- Technical walkthroughs of the probe engine methodology

---

## Weekly Cadence (One Person)

### Daily
- 5-10 strategic X replies to Tier 1 accounts
- Review approval queue via Discord

### 2x Per Week
- Probe-derived X thread (results from latest run)

### Weekly
- New probe run → results → distribute across platforms
- One Reddit text post (rotate subreddits)

### Monthly
- HN Show HN attempt with fresh angle

### As-Available
- TikTok (when Jena is ready)
- Long-form article on Medium/Dev.to/Hashnode

---

## Active Campaign: Dark States Arc Distribution

The Q16-Q18 arc needs to reach every platform:

| Platform | Format | Status |
|----------|--------|--------|
| X thread | 6-tweet thread with the hook | TODO |
| X article | Long-form write-up | TODO |
| Reddit r/artificial | Text post: "I asked 6 AIs to debunk a theory..." | TODO |
| Reddit r/philosophy | Text post: Gödel/structural limits angle | TODO |
| Medium | Full article with all 6 model responses | TODO |
| Dev.to | Technical walkthrough of probe methodology | TODO |
| HN | Show HN: "6 AIs tried to debunk a theory about their own limits" | TODO |
| GitHub | Q16-Q18 results committed to repo | DONE |

---

## Allies & Warm Leads

**Verified 2026-01-28** — Actually checked their tweets, not just summaries.

| Handle | Followers | Context | Status |
|--------|-----------|---------|--------|
| @PascalRaci39352 | 63 | Independently running 5 AIs, thoughtful AI engagement | Potential — verify with direct conversation |
| @IntuitMachine | — | AI philosophy content — best impression source | Engage consistently |

**Removed (not actual allies):**
- ~~@wordrefiner~~ — Book reviewer (jewelry, Sasquatch, church security). Irrelevant.
- ~~@seanspraguesr~~ — Claims to have "accidentally proved Riemann." Self-righteous.
- ~~@TheShashaankT~~ — Bot posting Hindi pseudo-spiritual "ULE framework" content.

---

## Target Accounts for Strategic Replies

### Tier 1: High-Value Researchers
| Account | Why | Angle |
|---------|-----|-------|
| @GaryMarcus | AI skeptic, debates limits constantly | BST formalizes what he intuits |
| @ylecun | Left Meta, founded AMI Labs | BST speaks to why the old approach hit walls |
| @fchollet | ARC Prize, intelligence measurement | BST explains why ARC is hard — structural limits |
| @ESYudkowsky | Alignment, existential risk | BST reframes alignment as a boundary problem |
| @melaniemitchell | AI complexity, emergence | BST maps emergence to boundary conditions |

### Tier 2: Community & Engagement Sources
| Account | Why |
|---------|-----|
| @IntuitMachine | AI philosophy content — best impression source |
| @PessimistsArc | Tech skepticism audience |
| @DrBrianKeating | Science communication — proven engagement |
| @Dan_Jeffries1 | AI/tech writer — already following |

**Removed from targets:**
- ~~@AnthropicAI, @OpenAI, @GoogleDeepMind~~ — Corporate accounts don't engage. Reply threads are noise.

---

## Growth Milestones

Milestones are based on engagement quality, not follower count.

| Milestone | Indicator | What It Means |
|-----------|-----------|---------------|
| First replication | Someone clones repo and runs probes independently | The methodology is reproducible |
| First structural critique | Someone engages with BST's formal claims, not just reacting | The work is being read seriously |
| First collaborator | Someone builds on BST or extends the probe methodology | The falsification surface is growing |
| Sustained discourse | Multiple threads per week where others discuss BST without prompting | The work has its own momentum |
| Academic engagement | A researcher with affiliation engages substantively | The credential barrier is breaking |

---

## What's Been Tried and Failed

| Approach | Result | Lesson |
|----------|--------|--------|
| Journal submissions | Desk reject — no affiliation | Need social proof before formal channels |
| ArXiv | Blocked — no endorsement | Same credential barrier |
| Direct researcher emails | Ignored | Cold outreach without social proof = deleted |
| Podcast pitches | Won't book unknowns | Need audience first |
| "Unified theory" framing | Triggers crank detectors | Lead with probes and results, not grand claims |

---

## Command Reference

### Daily Operations
```bash
python3 x_master.py daily              # Full daily routine (dry run)
python3 x_master.py daily-live         # Full daily routine (real)
python3 x_master.py engage             # Quick engagement scan
python3 x_master.py quote              # Find QT opportunities
python3 x_master.py analytics          # Dashboard
```

### Content Generation
```bash
python3 proof_engine.py all            # Run 6-model probe
python3 x_master.py threads            # Generate threads from probes
python3 x_master.py audio "text"       # ElevenLabs TTS
python3 x_master.py ingest             # Store probe data in Chroma
python3 x_master.py search "query"     # Semantic search over probes
```

### Approval Queue
```bash
python3 x_approval_queue.py review     # Interactive review
python3 x_approval_queue.py post       # Post approved items
python3 x_approval_queue.py stats      # Queue stats
python3 x_approval_queue.py pending    # List pending
```

### Multi-Platform Distribution
```bash
python3 article_formatter.py markdown  # Full markdown article
python3 article_formatter.py twitter   # X thread format
python3 article_formatter.py reddit    # Reddit text post
python3 article_formatter.py devto     # Dev.to with frontmatter
python3 article_formatter.py hn        # HN title + URL
python3 article_formatter.py medium    # Medium format
```

### Intelligence
```bash
python3 x_master.py web-scan           # Tavily web scan
python3 x_master.py discover <user>    # Find targets from account followers
```
