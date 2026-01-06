#!/usr/bin/env python3
"""
AI News Agent - RSS Ingest Script
Runs directly in GitHub Actions to bypass Vercel function timeout limits.
Fetches RSS feeds and inserts items into Supabase.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
PROJECT_DIR = Path(__file__).parent.parent
load_dotenv(PROJECT_DIR / '.env.local')

import feedparser
from supabase import create_client

# Configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
MAX_AGE_DAYS = 7

def normalize_url(url):
    """Normalize URL for deduplication"""
    if not url:
        return url
    # Remove trailing slashes and common tracking params
    url = url.rstrip('/')
    for param in ['utm_source', 'utm_medium', 'utm_campaign', 'ref']:
        if f'{param}=' in url:
            import re
            url = re.sub(f'[&?]{param}=[^&]*', '', url)
    return url

def fetch_rss_feed(url, source_name):
    """Fetch and parse an RSS feed"""
    try:
        feed = feedparser.parse(url)
        items = []

        cutoff_date = datetime.now() - timedelta(days=MAX_AGE_DAYS)

        for entry in feed.entries:
            # Parse published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_at = datetime(*entry.updated_parsed[:6]).isoformat()

            # Skip items older than MAX_AGE_DAYS
            if published_at:
                try:
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00').replace('+00:00', ''))
                    if pub_date < cutoff_date:
                        continue
                except:
                    pass

            # Get content
            content = ''
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].get('value', '')
            elif hasattr(entry, 'summary'):
                content = entry.summary
            elif hasattr(entry, 'description'):
                content = entry.description

            items.append({
                'title': entry.get('title', 'Untitled'),
                'url': normalize_url(entry.get('link', '')),
                'content': content[:10000] if content else None,
                'published_at': published_at
            })

        return items
    except Exception as e:
        print(f"  Error fetching {source_name}: {e}")
        return []

def main():
    print("=" * 50)
    print("AI News Agent - RSS Ingest")
    print("=" * 50)

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Missing Supabase credentials")
        sys.exit(1)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Get enabled sources
    print("\n1. Fetching sources...")
    result = supabase.table('sources').select('*').eq('enabled', True).execute()
    sources = result.data
    print(f"   Found {len(sources)} enabled sources")

    total_fetched = 0
    total_new = 0
    errors = []

    # Process each source
    print("\n2. Processing RSS feeds...")
    for source in sources:
        if source.get('type') != 'rss':
            print(f"   Skipping {source['name']} (type: {source.get('type')})")
            continue

        print(f"   Fetching: {source['name']}...")
        items = fetch_rss_feed(source['url'], source['name'])
        total_fetched += len(items)

        # Insert items
        new_count = 0
        for item in items:
            if not item['url'] or not item['title']:
                continue

            try:
                # Use upsert with ON CONFLICT DO NOTHING
                supabase.table('items').upsert({
                    'source_id': source['id'],
                    'url': item['url'],
                    'title': item['title'],
                    'content': item['content'],
                    'published_at': item['published_at']
                }, on_conflict='url', ignore_duplicates=True).execute()
                new_count += 1
            except Exception as e:
                if 'duplicate' not in str(e).lower() and '23505' not in str(e):
                    errors.append(f"{source['name']}: {str(e)[:50]}")

        total_new += new_count
        print(f"      -> {len(items)} items, {new_count} inserted")

        # Update last_fetched
        try:
            supabase.table('sources').update({
                'last_fetched': datetime.now().isoformat()
            }).eq('id', source['id']).execute()
        except:
            pass

    print("\n" + "=" * 50)
    print(f"SUMMARY: Fetched {total_fetched} items, {total_new} new")
    if errors:
        print(f"ERRORS: {len(errors)}")
        for err in errors[:5]:
            print(f"  - {err}")
    print("=" * 50)

if __name__ == '__main__':
    main()
