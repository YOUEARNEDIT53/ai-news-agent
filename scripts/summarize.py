#!/usr/bin/env python3
"""
AI News Agent - Summarization Script
Uses Claude to summarize new items that haven't been processed yet.
"""

import os
import sys
import json
import time
from pathlib import Path

from dotenv import load_dotenv
PROJECT_DIR = Path(__file__).parent.parent
load_dotenv(PROJECT_DIR / '.env.local')

from supabase import create_client
import anthropic

# Configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

SUMMARIZATION_PROMPT = """You are summarizing a single AI-related item for a daily briefing aimed at engineers building AI products.

Given the title and content below, return a JSON object with:
{
  "summary": "One clear sentence summarizing what this is about",
  "why_it_matters": "Max 25 words on why this is significant",
  "category": "research|product|engineering|business|policy|security",
  "topics": ["tag1", "tag2", "tag3"],
  "relevance_score": 0-100,
  "must_read": true/false,
  "hype_flag": true/false
}

Scoring:
- 90-100: Breakthrough result, major model release, critical security issue
- 75-89: Notable research with benchmark results, significant tool release
- 60-74: Useful update, interesting technique, industry news
- 40-59: Incremental improvement, niche application
- 0-39: Low relevance, promotional, or duplicate content

Rules:
- must_read = true ONLY for: frontier model releases, >10% benchmark improvements, critical security
- hype_flag = true if: vague claims, marketing language, no concrete details
- Return ONLY valid JSON, no markdown"""

def summarize_item(client, title, content, source_category='research'):
    """Use Claude to summarize an item"""
    truncated_content = content[:4000] if content else '(No content available - summarize based on title only)'

    message = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=500,
        system=SUMMARIZATION_PROMPT,
        messages=[{
            'role': 'user',
            'content': f"Title: {title}\n\nSource category: {source_category}\n\nContent:\n{truncated_content}"
        }]
    )

    response_text = message.content[0].text if message.content else ''

    try:
        # Extract JSON from response
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if not json_match:
            raise ValueError('No JSON found in response')

        result = json.loads(json_match.group())

        # Validate category
        valid_categories = ['research', 'product', 'engineering', 'business', 'policy', 'security']
        category = result.get('category', 'business')
        if category not in valid_categories:
            category = 'business'

        return {
            'summary': str(result.get('summary', 'No summary available')),
            'why_it_matters': str(result.get('why_it_matters', 'Significance unclear')),
            'category': category,
            'topics': result.get('topics', [])[:3],
            'relevance_score': min(100, max(0, int(result.get('relevance_score', 50)))),
            'must_read': bool(result.get('must_read', False)),
            'hype_flag': bool(result.get('hype_flag', False)),
        }
    except Exception as e:
        print(f"     Parse error: {e}")
        return {
            'summary': title,
            'why_it_matters': 'Unable to analyze significance',
            'category': 'business',
            'topics': [],
            'relevance_score': 30,
            'must_read': False,
            'hype_flag': False,
        }

def main():
    print("=" * 50)
    print("AI News Agent - Summarization")
    print("=" * 50)

    if not all([SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY]):
        print("ERROR: Missing required credentials")
        sys.exit(1)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Get existing summary IDs
    print("\n1. Checking existing summaries...")
    existing = supabase.table('summaries').select('item_id').execute()
    summarized_ids = set(s['item_id'] for s in existing.data)
    print(f"   Found {len(summarized_ids)} existing summaries")

    # Get items without summaries
    print("\n2. Fetching items to summarize...")
    items = supabase.table('items').select(
        'id,title,content,url,source:sources(name,category)'
    ).order('published_at', desc=True).limit(100).execute()

    items_to_summarize = [i for i in items.data if i['id'] not in summarized_ids][:50]
    print(f"   Found {len(items_to_summarize)} items to summarize")

    if not items_to_summarize:
        print("   No new items to summarize")
        return

    # Process items
    print("\n3. Summarizing items...")
    successful = 0
    failed = 0

    for i, item in enumerate(items_to_summarize):
        try:
            source = item.get('source')
            source_category = 'research'
            if source:
                if isinstance(source, list) and source:
                    source_category = source[0].get('category', 'research')
                elif isinstance(source, dict):
                    source_category = source.get('category', 'research')

            print(f"   [{i+1}/{len(items_to_summarize)}] {item['title'][:50]}...")
            summary = summarize_item(client, item['title'], item.get('content', ''), source_category)

            # Insert summary
            supabase.table('summaries').insert({
                'item_id': item['id'],
                'summary': summary['summary'],
                'why_it_matters': summary['why_it_matters'],
                'category': summary['category'],
                'topics': summary['topics'],
                'relevance_score': summary['relevance_score'],
                'must_read': summary['must_read'],
                'hype_flag': summary['hype_flag'],
            }).execute()

            successful += 1

            # Rate limiting
            if (i + 1) % 5 == 0:
                time.sleep(1)

        except Exception as e:
            print(f"     ERROR: {e}")
            failed += 1

    print(f"\n" + "=" * 50)
    print(f"SUMMARY: {successful} successful, {failed} failed")
    print("=" * 50)

if __name__ == '__main__':
    main()
