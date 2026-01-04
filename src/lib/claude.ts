import Anthropic from '@anthropic-ai/sdk';
import { SummarizationResult, ItemCategory } from '@/types';

// Lazy initialization to avoid build-time errors
let _anthropic: Anthropic | null = null;

function getAnthropicClient(): Anthropic {
  if (!_anthropic) {
    _anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
  }
  return _anthropic;
}

const SUMMARIZATION_PROMPT = `You are summarizing a single AI-related item for a daily briefing aimed at engineers building AI products.

Given the title and content below, return a JSON object with:
{
  "summary": "One clear sentence summarizing what this is about",
  "why_it_matters": "Max 25 words on why this is significant",
  "category": "research_breakthrough|lab_announcement|open_source|enterprise|industrial|community",
  "topics": ["tag1", "tag2", "tag3"],
  "relevance_score": 0-100,
  "must_read": true/false,
  "hype_flag": true/false,
  "priority_keywords": ["keyword1", "keyword2"],
  "major_model": "model name if mentioned, null otherwise"
}

Categories:
- research_breakthrough: Papers with SOTA results, benchmark improvements, new techniques
- lab_announcement: Anything from OpenAI, Anthropic, DeepMind, Meta AI, Google AI
- open_source: Framework releases, model weights, tools, libraries
- enterprise: Business AI, MLOps, cloud services, production deployments
- industrial: Manufacturing, robotics, automation, computer vision for industry
- community: Reddit discussions, HN threads, community projects

Priority detection - set priority_keywords if title/content contains:
- "breakthrough", "state-of-the-art", "SOTA", "surpasses", "outperforms"
- "release", "releases", "announces", "launches", "introducing"
- "open source", "weights available", "code available"

Major models to flag in major_model:
- GPT-4, GPT-5, Claude, Gemini, Llama, Mistral, Qwen, DeepSeek, Grok
- Any new model version announcements

Scoring:
- 90-100: Breakthrough result, major model release, critical security issue
- 75-89: Notable research with benchmark results, significant tool release
- 60-74: Useful update, interesting technique, industry news
- 40-59: Incremental improvement, niche application
- 0-39: Low relevance, promotional, or duplicate content

Rules:
- must_read = true ONLY for: frontier model releases, >10% benchmark improvements, critical security
- hype_flag = true if: vague claims, marketing language, no concrete details
- Return ONLY valid JSON, no markdown`;

export async function summarizeItem(
  title: string,
  content: string,
  sourceCategory: string
): Promise<SummarizationResult> {
  const truncatedContent = content.slice(0, 4000); // Limit input size
  const anthropic = getAnthropicClient();

  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 500,
    messages: [
      {
        role: 'user',
        content: `Title: ${title}

Source category: ${sourceCategory}

Content:
${truncatedContent || '(No content available - summarize based on title only)'}`,
      },
    ],
    system: SUMMARIZATION_PROMPT,
  });

  const responseText = message.content[0].type === 'text' ? message.content[0].text : '';

  try {
    // Extract JSON from response (handle potential markdown wrapping)
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('No JSON found in response');
    }

    const result = JSON.parse(jsonMatch[0]);

    // Validate and sanitize the result
    return {
      summary: String(result.summary || 'No summary available'),
      why_it_matters: String(result.why_it_matters || 'Significance unclear'),
      category: validateCategory(result.category),
      topics: Array.isArray(result.topics)
        ? result.topics.slice(0, 3).map(String)
        : [],
      relevance_score: Math.min(100, Math.max(0, Number(result.relevance_score) || 50)),
      must_read: Boolean(result.must_read),
      hype_flag: Boolean(result.hype_flag),
      priority_keywords: Array.isArray(result.priority_keywords)
        ? result.priority_keywords.slice(0, 5).map(String)
        : [],
      major_model: result.major_model ? String(result.major_model) : null,
    };
  } catch (error) {
    console.error('Failed to parse Claude response:', responseText, error);
    // Return a default result rather than failing
    return {
      summary: title,
      why_it_matters: 'Unable to analyze significance',
      category: 'community',
      topics: [],
      relevance_score: 30,
      must_read: false,
      hype_flag: false,
      priority_keywords: [],
      major_model: null,
    };
  }
}

function validateCategory(category: string): ItemCategory {
  const valid: ItemCategory[] = [
    'research_breakthrough', 'lab_announcement', 'open_source',
    'enterprise', 'industrial', 'community',
    // Keep old categories for backwards compatibility
    'research', 'product', 'engineering', 'policy', 'security', 'business'
  ];
  return valid.includes(category as ItemCategory)
    ? (category as ItemCategory)
    : 'community';
}

export async function summarizeBatch(
  items: Array<{ title: string; content: string; sourceCategory: string }>
): Promise<SummarizationResult[]> {
  // Process in parallel with rate limiting
  const results: SummarizationResult[] = [];
  const batchSize = 5;

  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(
      batch.map((item) =>
        summarizeItem(item.title, item.content, item.sourceCategory)
      )
    );
    results.push(...batchResults);

    // Small delay between batches to respect rate limits
    if (i + batchSize < items.length) {
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  }

  return results;
}
