# AI News Agent

An automated AI/ML news aggregation, summarization, and podcast generation system.

## Features

- **22 Diverse Sources** - Research papers, lab blogs, enterprise news, robotics, and community discussions
- **AI-Powered Summarization** - Claude claude-sonnet-4 analyzes and scores each article (0-100)
- **Daily Email Digest** - Curated sections: Must Know, Worth a Look, Quick Hits
- **Podcast Generation** - Audio briefings with two AI hosts (Marcus & Priya)
- **Transparency** - Full explainability of scoring criteria and source selection

## Quick Start

```bash
# Install dependencies
npm install

# Set up environment (see .env.example)
cp .env.example .env.local

# Run development server
npm run dev

# Run the full pipeline
curl -X POST http://localhost:3000/api/ingest
curl -X POST http://localhost:3000/api/summarize
curl -X POST http://localhost:3000/api/digest
curl -X POST http://localhost:3000/api/podcast
```

## News Sources

| Category | Sources |
|----------|---------|
| Research | arXiv (ML, AI, NLP, CV, Robotics, stat.ML), HuggingFace Papers |
| Lab Blogs | OpenAI, DeepMind, Google Research, Meta AI, Microsoft Research |
| Enterprise | VentureBeat, Ars Technica, AWS ML, NVIDIA, MLOps Community |
| Robotics | Robot Report, Robohub, Roboflow, Automation World |
| Community | r/MachineLearning, r/LocalLLaMA, Hacker News |

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for complete documentation including:

- Data flow pipeline
- Scoring & classification algorithms
- How to add/edit sources
- Database schema
- API reference
- Troubleshooting guide

## Tech Stack

- **Framework:** Next.js 16
- **Database:** Supabase (PostgreSQL)
- **AI:** Anthropic Claude claude-sonnet-4
- **Email:** Resend
- **Audio:** Microsoft Edge TTS
- **Deployment:** Vercel (optional)

## Environment Variables

```env
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
ANTHROPIC_API_KEY=
RESEND_API_KEY=
DIGEST_EMAIL_TO=
DIGEST_EMAIL_FROM=
CRON_SECRET=
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ingest` | POST | Fetch articles from all sources |
| `/api/summarize` | POST | Summarize unsummarized articles |
| `/api/digest` | POST/GET | Generate/retrieve daily digest |
| `/api/podcast` | POST | Generate audio podcast |

## Scoring Criteria

| Score | Meaning |
|-------|---------|
| 90-100 | Breakthrough, major model release, critical security |
| 75-89 | Notable research, significant tool release |
| 60-74 | Useful update, interesting technique |
| 40-59 | Incremental improvement, niche application |
| 0-39 | Low relevance, promotional content |

## License

MIT
