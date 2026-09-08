# Idea Graveyard

> **Tagline:** Creators don't run out of ideas. They lose them.

---

## Inspiration

Every creator has an idea graveyard — a messy backlog of half-written scripts, Notion pages, spreadsheets of *"maybe someday"* titles, and voice notes from 2 AM brainstorms that never saw the light of day. 

The universal challenge for creators isn't generating *more* ideas. The problem is figuring out: **Which forgotten idea is actually worth making *now*?**

Creators waste hours brainstorming new concepts from scratch while sitting on dozens of dormant ideas that are more relevant today than when they were originally conceived. The creator landscape shifts constantly — new technology emerges, audience interests mature, and market gaps open up. An idea that was "too early" or under-appreciated six months ago might be the exact breakthrough topic today.

We built **Idea Graveyard** around a simple question:  
*What if your forgotten ideas could monitor the market and tell you when they are ready to be made?*

---

## What it does

**Idea Graveyard** is an editorial research workspace that centralizes abandoned content ideas, scores them against your actual content performance baseline, and resurrects the highest-potential concepts with actionable production kits.

1. **Ingest & Fingerprint:** Import ideas from CSV files, notes, or manual inputs. Every idea is hashed with a deterministic SHA-256 fingerprint to eliminate duplicates.
2. **Deterministic Multi-Factor Scoring:** Each idea is evaluated across five distinct dimensions to surface its real-world relevance.
3. **Resurrection Discovery:** The dashboard immediately isolates top resurrection candidates with transparent score breakdowns.
4. **Actionable Resurrection Brief:** With one click, Google Gemini generates an editorial package:
   - **Why Now Analysis:** Explains the macro shifts and market timing that make the topic urgent.
   - **High-CTR Hooks:** Scroll-stopping opening angles and titles tailored to the creator's voice.
   - **Structured Outline:** 4–6 core sections with concrete talking points and filming notes.

---

## How we built it

We built Idea Graveyard as a modular, high-reliability stack combining a **FastAPI** backend, **PostgreSQL** database, and a **React + TypeScript + Vite** frontend.

### 1. Transparent Mathematical Scoring Engine
Rather than relying on an opaque "black-box" prompt, we separated qualitative semantic reasoning from mathematical scoring. Google Gemini evaluates categorical sub-scores, while our deterministic backend calculates the final score using a weighted linear combination:

$$\text{Relevance Score} = \sum_{i=1}^{5} w_i \cdot s_i$$

$$\text{Score} = 0.30 \cdot \text{AudienceFit} + 0.25 \cdot \text{ContentFit} + 0.20 \cdot \text{Freshness} + 0.15 \cdot \text{HistoricalFit} + 0.10 \cdot \text{SemanticOpportunity}$$

Where each sub-score $s_i \in [0, 100]$:
- **Audience Fit ($30\%$):** Semantic overlap with recent high-performing viewer demand.
- **Content Fit ($25\%$):** Alignment with the creator's current core niche.
- **Freshness ($20\%$):** Timeliness and relevance in the current cultural and technological climate.
- **Historical Fit ($15\%$):** Track record of similar themes in the creator's past library.
- **Semantic Opportunity ($10\%$):** Room for a unique, unexploited angle.

### 2. Reliable AI Architecture
- **LLM Provider:** Google Gemini (`gemini-2.5-flash-lite`) integrated natively via the `google-generativeai` SDK.
- **Strict Pydantic Validation:** Every AI generation is parsed and validated against strict schemas with field-level constraints ($s_i \in [0, 100]$), with automated retries on malformed syntax.
- **State Machine Integrity:** Ideas transition through a strict state machine:
  $$\text{Dormant} \longrightarrow \text{Reconsidering} \longrightarrow \text{Resurrected}$$
  If an API failure occurs during generation, the transaction automatically rolls back to $\text{Dormant}$ to prevent hanging states.

### 3. Editorial-First UI Design
We deliberately stepped away from generic "AI dashboard" tropes. Using a custom Vanilla CSS design system, we crafted an editorial research workspace with a distraction-free aesthetic, dark-mode styling, responsive radar progress bars, and progressive disclosure cards.

---

## Challenges we ran into

1. **Ensuring 100% Deterministic & Reliable JSON:** LLMs frequently wrap responses in markdown fences or append conversational preambles. We engineered a multi-stage parser with regex stripping and Pydantic validation that catches malformed outputs and executes a strict prompt retry when necessary.
2. **Preventing State Corruption During Failures:** Network drops or API timeouts during the resurrection phase could leave ideas stranded in `reconsidering` status. We implemented atomic database rollback handling to preserve clean state transitions.
3. **Designing for Zero-State & Scale:** Content creators have backlogs ranging from 5 to 500 ideas. We optimized CSV ingestion using bulk fingerprint lookups to avoid $O(N)$ database round-trips.

---

## Accomplishments that we're proud of

- **100% Functional End-to-End System:** From database ingestion to real-time Gemini analysis and interactive React UI, every single button and workflow runs live and produces real results.
- **Deterministic Math Over AI Hallucinations:** We proved that AI works best when bounded by deterministic mathematics—reproducible, transparent, and grounded in real data.
- **Comprehensive Test Suite:** Authored a suite of 17 unit and integration tests covering scoring formulas, edge-case clamping, schema validation, and deduplication logic.
- **High-Utility Content Briefs:** The generated Resurrection Briefs deliver genuinely insightful angles and hooks rather than generic bullet points.

---

## What we learned

- **AI is strongest at synthesis, code is best at computation:** Keeping arithmetic in Python and qualitative analysis in LLMs creates a system that users can trust.
- **Schema enforcement is mandatory:** Runtime validation with Pydantic transformed unpredictable text generation into rock-solid software pipelines.
- **Creative tools need quiet interfaces:** Subtle, content-focused editorial design helps creators stay in deep focus rather than feeling overwhelmed by complex telemetry.

---

## What's next for Idea Graveyard

- **Direct Platform Integrations:** Connect directly with YouTube Studio, Substack, and Spotify for Podcasters APIs to automatically pull live audience retention metrics.
- **Autonomous Trend Radar:** Ingest Google Trends and Twitter/X conversation spikes to dynamically re-evaluate the *Freshness* and *Why Now* scores of dormant ideas on a weekly schedule.
- **1-Click Browser Extension:** Save ideas straight into the Graveyard from Twitter threads, Reddit discussions, or YouTube comment sections.
- **Collaborative Workspaces:** Support for multi-creator teams, podcast co-hosts, and editorial boards to vote on resurrection candidates.
