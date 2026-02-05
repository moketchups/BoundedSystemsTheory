# X Algorithm Insights for Growth

From `twitter/the-algorithm` source code analysis.

---

## Ranking Signals (What Gets You Seen)

### High-Value Actions (Features + Labels in ML)
| Signal | Weight | Notes |
|--------|--------|-------|
| **Tweet Favorite (Like)** | Highest | Primary engagement signal |
| **Retweet** | High | Amplification |
| **Quote Tweet** | High | Engagement + commentary |
| **Tweet Reply** | Medium-High | Conversation signal |
| **Author Follow** | High | Trust/interest signal |

### Medium-Value Actions
| Signal | Notes |
|--------|-------|
| Tweet Click | Opened the tweet detail |
| Video Watch | Attention time |
| Tweet Share | Distribution intent |
| Notification Open | Push engagement |
| Bookmark | Save for later |

### Negative Signals (Hurt Your Reach)
- Unfollow
- Mute
- Block
- Unlike
- "Not interested"
- Report

---

## SimClusters: How X Groups Users

X uses **community detection** based on follow patterns:

1. **Producer-Producer Similarity**: Users who have similar followers get clustered together
2. **~145,000 communities** detected from follow graph
3. **KnownFor**: Each producer is "known for" specific clusters
4. **InterestedIn**: Each consumer's interests mapped to clusters

### BST Target Clusters
- AI/ML researchers
- Philosophy/consciousness
- Tech critics
- Founders/builders
- Science communicators

**Implication**: Get followed by people in these clusters → your content shows to similar users.

---

## Tweet Embeddings (Real-Time)

When a tweet is created:
1. Starts with empty embedding vector
2. Updated **every time someone likes it**
3. The liker's InterestedIn vector is added to the tweet vector
4. This is why early engagement matters - shapes who sees it next

---

## Heavy Ranker (Neural Net)

Final ranking uses:
- **real-graph**: Predicts likelihood of interaction between users
- **tweepcred**: PageRank-style user reputation score
- **SimClusters embeddings**: Community relevance
- **Engagement velocity**: How fast is it getting engagement

---

## Practical Takeaways

### To Maximize Reach:
1. **Get early likes** from users in your target clusters (AI/philosophy/tech)
2. **Replies > Quote Tweets > Likes** for engagement
3. **Timing matters** - tweet embeddings are built in first hours
4. **Build tweepcred** - consistent quality > viral spikes
5. **Avoid negative signals** - don't trigger unfollows/mutes

### For BST Growth:
1. Find conversations in target clusters (AI consciousness, limits, Gödel)
2. Reply with value (not drive-by promotion)
3. Get follows from cluster members → algorithm starts serving you to similar users
4. Quote tweets from cluster influencers with substantive additions

### Engagement Criteria (from AutoXAI patterns)
- Target tweets with < 50 replies (not too crowded)
- < 24 hours old (still getting impressions)
- Minimum 50 chars (substantive content to respond to)
- User has 100+ followers (some reach)

---

## Key Files in twitter/the-algorithm

| Component | Location | What It Does |
|-----------|----------|--------------|
| SimClusters | `src/scala/com/twitter/simclusters_v2/` | Community detection |
| Heavy Ranker | `home-mixer/` | Final feed ranking |
| real-graph | `src/scala/com/twitter/interaction_graph/` | User interaction prediction |
| tweepcred | `src/scala/com/twitter/graph/batch/job/tweepcred/` | User reputation |
| Retrieval Signals | `RETREIVAL_SIGNALS.md` | All input signals |
