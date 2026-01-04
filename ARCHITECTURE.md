# AI News Agent - Architecture & Transparency Report

**Version:** 1.0.0
**Last Updated:** 2026-01-04
**Maintainer:** youearnedit@gmail.com

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Data Flow Pipeline](#data-flow-pipeline)
3. [News Sources](#news-sources)
4. [Scoring & Classification](#scoring--classification)
5. [Digest Generation](#digest-generation)
6. [Podcast Generation](#podcast-generation)
7. [How to Recreate](#how-to-recreate)
8. [How to Add/Edit Sources](#how-to-addedit-sources)
9. [API Reference](#api-reference)
10. [Database Schema](#database-schema)
11. [Troubleshooting](#troubleshooting)

---

## System Overview

The AI News Agent is an automated news aggregation and summarization system that:

1. **Ingests** articles from 22 diverse AI/ML news sources
2. **Summarizes** each article using Claude AI (claude-sonnet-4)
3. **Scores** articles for relevance (0-100)
4. **Generates** daily email digests with curated sections
5. **Creates** podcast-style audio briefings using Edge TTS

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        NEWS SOURCES (22)                        │
│  Research │ Lab Blogs │ Enterprise │ Robotics │ Community       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INGESTION PIPELINE                          │
│  /api/ingest → RSS Parser → 7-day filter → Deduplication        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUMMARIZATION PIPELINE                       │
│  /api/summarize → Claude API → Category + Score + Summary       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DIGEST GENERATION                          │
│  /api/digest → Section Sorting → Email via Resend               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PODCAST GENERATION                          │
│  /api/podcast → Script Generation → Edge TTS → Email Delivery   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Pipeline

### Step 1: Ingestion (`/api/ingest`)

**File:** `src/app/api/ingest/route.ts`

- Fetches all enabled sources from Supabase
- Processes sources in batches of 4 (parallel)
- For RSS sources: Uses `rss-parser` library
- For scrape sources: Uses `cheerio` for HTML parsing
- Filters to articles from the last 7 days
- Deduplicates by normalized URL
- Stores in `items` table

**Transparency:** Only articles with valid publish dates within 7 days are included. URLs are normalized (tracking params removed) before duplicate checking.

### Step 2: Summarization (`/api/summarize`)

**File:** `src/lib/claude.ts`

- Processes unsummarized items in batches of 5
- Each item sent to Claude claude-sonnet-4 with structured prompt
- Returns: summary, why_it_matters, category, topics, relevance_score, must_read, hype_flag

**Explainability - Scoring Criteria:**

| Score Range | Meaning |
|-------------|---------|
| 90-100 | Breakthrough result, major model release, critical security issue |
| 75-89 | Notable research with benchmark results, significant tool release |
| 60-74 | Useful update, interesting technique, industry news |
| 40-59 | Incremental improvement, niche application |
| 0-39 | Low relevance, promotional, or duplicate content |

**Category Classification:**

| Claude Category | Database Category | Description |
|----------------|-------------------|-------------|
| research_breakthrough | research | Papers with SOTA results, benchmark improvements |
| lab_announcement | product | News from OpenAI, Anthropic, DeepMind, Meta AI |
| open_source | engineering | Framework releases, model weights, tools |
| enterprise | business | Business AI, MLOps, cloud services |
| industrial | engineering | Manufacturing, robotics, automation |
| community | business | Reddit discussions, HN threads |

### Step 3: Digest Generation (`/api/digest`)

**File:** `src/app/api/digest/route.ts`

- Queries all summarized items
- Sorts by relevance_score descending
- Categorizes into sections using relative thresholds:
  - **Must Know:** `must_read=true` OR score >= 70% of max score
  - **Worth a Look:** Score between 40-70% of max
  - **Quick Hits:** Score below 40% of max
- Saves digest to database
- Sends email via Resend API

### Step 4: Podcast Generation (`/api/podcast`)

**File:** `src/app/api/podcast/route.ts`

- Fetches latest digest content
- Generates conversational script for two hosts (Marcus & Priya)
- Converts to audio using Edge TTS (free Microsoft API)
- Sends MP3 attachment via email

---

## News Sources

### Current Sources (22 total)

#### Research (4 sources)
| Source | URL | Type |
|--------|-----|------|
| arXiv ML+AI+NLP | https://rss.arxiv.org/rss/cs.LG+cs.AI+cs.CL | RSS |
| arXiv CV+Robotics | https://rss.arxiv.org/rss/cs.CV+cs.RO | RSS |
| arXiv stat.ML | https://rss.arxiv.org/rss/stat.ML | RSS |
| HuggingFace Daily Papers | https://papers.takara.ai/api/feed | RSS |

#### Lab Blogs (6 sources)
| Source | URL | Type |
|--------|-----|------|
| OpenAI News | https://openai.com/news/rss.xml | RSS |
| Google DeepMind | https://deepmind.google/blog/rss.xml | RSS |
| Google Research | https://research.google/blog/rss | RSS |
| Meta AI | https://research.facebook.com/feed/ | RSS |
| Microsoft Research | https://www.microsoft.com/en-us/research/feed/ | RSS |
| HuggingFace Blog | https://huggingface.co/blog/feed.xml | RSS |

#### Ecosystem/Enterprise (9 sources)
| Source | URL | Type |
|--------|-----|------|
| VentureBeat AI | https://venturebeat.com/category/ai/feed/ | RSS |
| Ars Technica AI | https://arstechnica.com/ai/feed/ | RSS |
| AWS ML Blog | https://aws.amazon.com/blogs/machine-learning/feed/ | RSS |
| NVIDIA Developer Blog | https://developer.nvidia.com/blog/feed | RSS |
| MLOps Community | https://mlops.community/feed/ | RSS |
| The Robot Report | https://www.therobotreport.com/feed | RSS |
| Robohub | https://robohub.org/feed | RSS |
| Automation World | https://www.automationworld.com/__rss/website/all | RSS |
| Roboflow Blog | https://blog.roboflow.com/rss | RSS |

#### Community (3 sources)
| Source | URL | Type |
|--------|-----|------|
| r/MachineLearning | https://www.reddit.com/r/MachineLearning/.rss | RSS |
| r/LocalLLaMA | https://www.reddit.com/r/LocalLLaMA/.rss | RSS |
| HN LLM+AI | https://hnrss.org/newest?q=LLM+OR+GPT&points=50 | RSS |

---

## Scoring & Classification

### Relevance Score Algorithm

The relevance score (0-100) is determined by Claude based on:

1. **Impact Magnitude**
   - Breakthrough results (+30-40 points)
   - Benchmark improvements (+20-30 points)
   - New capabilities (+15-25 points)

2. **Source Authority**
   - Major lab announcements (+20 points)
   - Peer-reviewed research (+15 points)
   - Community discussions (+5 points)

3. **Practical Applicability**
   - Production-ready tools (+20 points)
   - Code/weights available (+15 points)
   - Tutorial/guide (+10 points)

4. **Negative Factors**
   - Marketing language (-20 points)
   - Vague claims without data (-15 points)
   - Duplicate/rehashed content (-30 points)

### Hype Detection

Articles are flagged as "hype" if they contain:
- Vague claims without concrete benchmarks
- Marketing language ("revolutionary", "game-changing")
- No technical details or reproducibility info
- Clickbait titles

### Must-Read Criteria

An article is marked `must_read=true` only if:
- Frontier model release (GPT-5, Claude 4, etc.)
- >10% improvement on major benchmarks
- Critical security vulnerability disclosure
- Major open-source model weights release

---

## Digest Generation

### Section Allocation

```
MUST KNOW (max 3 items)
├── must_read=true items
└── Top scorers (>= 70% of max score)

WORTH A LOOK (max 7 items)
└── Scores between 40-70% of max

QUICK HITS (max 10 items)
└── Scores below 40% of max
```

### Email Format

```
Subject: AI Briefing - January 4, 2026

## Must Know
[Top 3 most important items with full summaries]

## Worth a Look
[7 notable items with brief summaries]

## Quick Hits
[10 items as bullet points]
```

---

## Podcast Generation

### Host Personas

**Marcus** (Technical Co-host)
- Former ML engineer turned tech journalist
- Explains concepts through memorable analogies
- Gets excited about elegant solutions
- Verbal tics: "So here's the thing...", "Wait, it gets better..."

**Priya** (Applications Co-host)
- Background in product management at ML startups
- Focuses on practical implications
- Keeps receipts on company announcements
- Verbal tics: "Okay but here's my question...", "Let's be real..."

### Audio Generation

- **Engine:** Microsoft Edge TTS (free tier)
- **Voices:** en-US-GuyNeural (Marcus), en-US-AriaNeural (Priya)
- **Format:** MP3, ~128kbps
- **Duration:** Typically 5-10 minutes

---

## How to Recreate

### Prerequisites

- Node.js 18+
- npm or pnpm
- Supabase account
- Anthropic API key
- Resend API key

### Step 1: Clone and Install

```bash
git clone https://github.com/YOUEARNEDIT53/ai-news-agent.git
cd ai-news-agent
npm install
```

### Step 2: Environment Setup

Create `.env.local`:

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_key

# Resend Email
RESEND_API_KEY=your_resend_key
DIGEST_EMAIL_TO=your_email@example.com
DIGEST_EMAIL_FROM=AI News Agent <onboarding@resend.dev>

# Cron secret
CRON_SECRET=your_random_secret
```

### Step 3: Database Setup

Run migrations in Supabase SQL editor:

```bash
# Or use Supabase CLI
supabase db push
```

### Step 4: Run Locally

```bash
npm run dev
```

### Step 5: Test Pipeline

```bash
# Ingest articles
curl -X POST http://localhost:3000/api/ingest

# Summarize
curl -X POST http://localhost:3000/api/summarize

# Generate digest
curl -X POST http://localhost:3000/api/digest

# Generate podcast
curl -X POST http://localhost:3000/api/podcast
```

---

## How to Add/Edit Sources

### Adding a New Source

**Option 1: Via Supabase Dashboard**

1. Go to Supabase Dashboard > Table Editor > sources
2. Click "Insert row"
3. Fill in:
   - `name`: Display name (e.g., "TechCrunch AI")
   - `url`: RSS feed URL
   - `type`: `rss` | `scrape` | `api`
   - `category`: `research` | `lab` | `ecosystem`
   - `enabled`: `true`

**Option 2: Via SQL**

```sql
INSERT INTO sources (name, url, type, category) VALUES
  ('TechCrunch AI', 'https://techcrunch.com/category/artificial-intelligence/feed/', 'rss', 'ecosystem');
```

**Option 3: Via REST API**

```bash
curl -X POST "https://YOUR_PROJECT.supabase.co/rest/v1/sources" \
  -H "apikey: YOUR_SERVICE_KEY" \
  -H "Authorization: Bearer YOUR_SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "type": "rss", "category": "ecosystem"}'
```

### Disabling a Source

```sql
UPDATE sources SET enabled = false WHERE name = 'Source Name';
```

### Testing a New RSS Feed

Before adding, verify the feed works:

```bash
# Check if URL returns valid RSS
curl -s "https://example.com/feed/" | head -20

# Test with rss-parser
npx rss-parser "https://example.com/feed/"
```

### Source Categories

| Category | Use For |
|----------|---------|
| `research` | Academic papers, arXiv, research blogs |
| `lab` | Official company blogs (OpenAI, Google, etc.) |
| `ecosystem` | News sites, community content, tools |

---

## API Reference

### POST /api/ingest

Fetches new articles from all enabled sources.

**Headers:**
- `x-cron-secret`: Your CRON_SECRET (optional for manual calls)

**Response:**
```json
{
  "success": true,
  "summary": {
    "sources_processed": 22,
    "items_fetched": 109,
    "items_new": 109,
    "errors": 4
  }
}
```

### POST /api/summarize

Summarizes unsummarized articles (50 per call).

**Response:**
```json
{
  "success": true,
  "result": {
    "processed": 50,
    "successful": 50,
    "failed": 0
  }
}
```

### POST /api/digest

Generates and emails the daily digest.

**Body (optional):**
```json
{
  "date": "2026-01-04",
  "send_email": true
}
```

### POST /api/podcast

Generates and emails the podcast audio.

### GET /api/digest

Returns the latest digest content.

---

## Database Schema

### sources
```sql
CREATE TABLE sources (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  url TEXT NOT NULL UNIQUE,
  type source_type NOT NULL,      -- 'rss' | 'api' | 'scrape'
  category source_category NOT NULL,  -- 'research' | 'lab' | 'ecosystem'
  enabled BOOLEAN DEFAULT true,
  last_fetched TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### items
```sql
CREATE TABLE items (
  id UUID PRIMARY KEY,
  source_id UUID REFERENCES sources(id),
  url TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  content TEXT,
  published_at TIMESTAMPTZ,
  fetched_at TIMESTAMPTZ DEFAULT NOW()
);
```

### summaries
```sql
CREATE TABLE summaries (
  id UUID PRIMARY KEY,
  item_id UUID UNIQUE REFERENCES items(id),
  summary TEXT NOT NULL,
  why_it_matters TEXT NOT NULL,
  category item_category NOT NULL,
  topics JSONB DEFAULT '[]',
  relevance_score INTEGER CHECK (0-100),
  must_read BOOLEAN DEFAULT false,
  hype_flag BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### digests
```sql
CREATE TABLE digests (
  id UUID PRIMARY KEY,
  date DATE NOT NULL UNIQUE,
  content JSONB NOT NULL,
  email_sent BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Troubleshooting

### Common Issues

**Issue:** Only getting articles from one source
- **Cause:** Other RSS feeds may be broken or timing out
- **Fix:** Check ingestion response for errors, test feeds individually

**Issue:** Summarization failing with enum errors
- **Cause:** Claude returning categories not in database
- **Fix:** Category mapping in `src/lib/claude.ts` handles this

**Issue:** No articles in digest
- **Cause:** No articles scored above threshold
- **Fix:** Check if summarization ran, verify items exist in database

**Issue:** Podcast audio not generating
- **Cause:** Edge TTS service may be rate limited
- **Fix:** Wait and retry, check network connectivity

### Logs

Check server logs for detailed error messages:

```bash
npm run dev  # Logs appear in terminal
```

### Manual Database Queries

```sql
-- Check recent items
SELECT title, url, fetched_at FROM items ORDER BY fetched_at DESC LIMIT 10;

-- Check summarization status
SELECT COUNT(*) as total,
       COUNT(s.id) as summarized
FROM items i
LEFT JOIN summaries s ON i.id = s.item_id;

-- Check source health
SELECT name, last_fetched, enabled FROM sources ORDER BY last_fetched DESC;
```

---

## Changelog

### 2026-01-04
- Fixed category mapping bug in summarization
- Added 22 diverse sources (research, labs, enterprise, community)
- Improved error handling in RSS parsing
- Added this documentation

---

## License

MIT License - See LICENSE file for details.
