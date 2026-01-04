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

const SUMMARIZATION_PROMPT = `You are summarizing a single AI-related item for a daily briefing.

Given the title and content below, return a JSON object with:
{
  "summary": "One clear sentence summarizing what this is about",
  "why_it_matters": "Max 25 words on why this is significant (for someone building AI products)",
  "category": "research|product|engineering|policy|security|business",
  "topics": ["tag1", "tag2", "tag3"],
  "relevance_score": 0-100,
  "must_read": true/false,
  "hype_flag": true/false
}

Scoring guidelines:
- 80-100: Major model release, breakthrough result, significant policy change
- 60-79: Notable research, useful new tool, important industry news
- 40-59: Incremental improvement, niche application, minor update
- 0-39: Low relevance, promotional content, or duplicate of common knowledge

Rules:
- must_read = true ONLY for: new frontier model releases, significant benchmark improvements (>10%), major policy/regulation, critical security issues
- hype_flag = true if: claims lack support in provided text, vague/marketing language, no concrete details, or extraordinary claims without evidence
- If hype_flag is true, lower relevance_score accordingly
- Do not add facts not present in the text
- topics should be lowercase, max 3 tags
- Return ONLY valid JSON, no markdown or explanation`;

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
    };
  } catch (error) {
    console.error('Failed to parse Claude response:', responseText, error);
    // Return a default result rather than failing
    return {
      summary: title,
      why_it_matters: 'Unable to analyze significance',
      category: 'research',
      topics: [],
      relevance_score: 30,
      must_read: false,
      hype_flag: false,
    };
  }
}

function validateCategory(category: string): ItemCategory {
  const valid: ItemCategory[] = ['research', 'product', 'engineering', 'policy', 'security', 'business'];
  return valid.includes(category as ItemCategory)
    ? (category as ItemCategory)
    : 'research';
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
