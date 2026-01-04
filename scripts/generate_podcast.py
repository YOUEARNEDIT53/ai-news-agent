#!/usr/bin/env python3
"""
AI News Agent - Daily Podcast Generator
Generates a two-host podcast from the daily digest using Podcastfy
"""

import os
import sys
import json
import asyncio
import shutil
from datetime import datetime
from pathlib import Path

# Add local ffmpeg to PATH
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
BIN_DIR = PROJECT_DIR / 'bin'
os.environ['PATH'] = str(BIN_DIR) + ':' + os.environ.get('PATH', '')

# Load environment variables
from dotenv import load_dotenv
load_dotenv(PROJECT_DIR / '.env.local')

from podcastfy.client import generate_podcast
import requests
from supabase import create_client

# Configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
DIGEST_EMAIL_TO = os.getenv('DIGEST_EMAIL_TO', 'youearnedit@gmail.com')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Output directory for podcasts
OUTPUT_DIR = Path(__file__).parent.parent / 'podcasts'
OUTPUT_DIR.mkdir(exist_ok=True)


def get_latest_digest():
    """Fetch the latest digest from Supabase"""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    result = supabase.table('digests') \
        .select('*') \
        .order('date', desc=True) \
        .limit(1) \
        .execute()

    if result.data:
        return result.data[0]
    return None


def format_digest_for_podcast(digest):
    """Convert digest JSON to a text format suitable for podcast generation"""
    content = digest['content']
    date = digest['date']

    text = f"""# AI News Briefing for {date}

Welcome to your daily AI news briefing. Today we're covering the most important developments in artificial intelligence.

## MUST KNOW - The Top Stories

"""

    for item in content.get('must_know', []):
        text += f"""### {item['title']}
{item['summary']}

Why this matters: {item['why_it_matters']}

"""

    text += "\n## WORTH A LOOK - Notable Developments\n\n"

    for item in content.get('worth_a_look', []):
        text += f"""### {item['title']}
{item['summary']}

Why this matters: {item['why_it_matters']}

"""

    text += "\n## QUICK HITS - Brief Updates\n\n"

    for item in content.get('quick_hits', []):
        text += f"- **{item['title']}**: {item['summary']}\n"

    text += """

## Wrap Up

That's your AI briefing for today. Stay informed, stay curious, and we'll see you tomorrow with more developments from the world of artificial intelligence.
"""

    return text


def generate_podcast_audio(text_content, output_path):
    """Generate podcast audio using Podcastfy with Edge TTS (free)"""

    # Custom conversation config for news briefing style
    conversation_config = {
        "word_count": 1500,
        "conversation_style": ["informative", "professional", "engaging"],
        "podcast_name": "AI News Briefing",
        "podcast_tagline": "Your daily dose of AI developments",
        "creativity": 0.7,
        "roles_person1": "Host",
        "roles_person2": "Co-host",
        "dialogue_structure": [
            "Introduction",
            "Must Know Stories",
            "Worth A Look",
            "Quick Hits",
            "Closing"
        ],
        "engagement_techniques": [
            "brief commentary",
            "highlighting key points",
            "making connections between stories"
        ],
        "output_language": "English"
    }

    try:
        # Generate podcast using Edge TTS (free) and Claude for conversation
        audio_file = generate_podcast(
            text=text_content,
            tts_model="edge",  # Free Microsoft Edge TTS
            llm_model_name="anthropic/claude-sonnet-4-20250514",  # Use Claude
            api_key_label="ANTHROPIC_API_KEY",
            conversation_config=conversation_config
        )

        # Move the generated file to our desired output path
        if audio_file and Path(audio_file).exists():
            shutil.move(audio_file, output_path)
            return str(output_path)
        return audio_file

    except Exception as e:
        print(f"Error with custom config: {e}")
        import traceback
        traceback.print_exc()
        # Try simpler approach without conversation_config
        audio_file = generate_podcast(
            text=text_content,
            tts_model="edge",
            llm_model_name="anthropic/claude-sonnet-4-20250514",
            api_key_label="ANTHROPIC_API_KEY"
        )
        if audio_file and Path(audio_file).exists():
            shutil.move(audio_file, output_path)
            return str(output_path)
        return audio_file


def send_podcast_email(audio_path, date):
    """Send the podcast as an email attachment using Resend"""

    # Read the audio file
    with open(audio_path, 'rb') as f:
        audio_data = f.read()

    import base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    response = requests.post(
        'https://api.resend.com/emails',
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'from': 'AI News Agent <onboarding@resend.dev>',
            'to': DIGEST_EMAIL_TO,
            'subject': f'🎙️ AI News Podcast - {date}',
            'html': f'''
                <h1>Your AI News Podcast is Ready!</h1>
                <p>Listen to today's AI briefing in podcast format.</p>
                <p>Date: {date}</p>
                <p>The audio file is attached to this email.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Generated by AI News Agent using Podcastfy
                </p>
            ''',
            'attachments': [{
                'filename': f'ai-briefing-{date}.mp3',
                'content': audio_base64
            }]
        }
    )

    if response.status_code == 200:
        print(f"Podcast email sent successfully to {DIGEST_EMAIL_TO}")
        return True
    else:
        print(f"Failed to send email: {response.text}")
        return False


def main():
    print("=" * 50)
    print("AI News Agent - Podcast Generator")
    print("=" * 50)

    # Get latest digest
    print("\n1. Fetching latest digest...")
    digest = get_latest_digest()

    if not digest:
        print("No digest found!")
        sys.exit(1)

    date = digest['date']
    print(f"   Found digest for {date}")

    # Format for podcast
    print("\n2. Formatting digest for podcast...")
    text_content = format_digest_for_podcast(digest)
    print(f"   Generated {len(text_content)} characters of content")

    # Generate podcast
    output_path = OUTPUT_DIR / f'ai-briefing-{date}.mp3'
    print(f"\n3. Generating podcast audio...")
    print("   Using Edge TTS (free)")

    try:
        audio_file = generate_podcast_audio(text_content, output_path)
        print(f"   Podcast saved to: {audio_file}")
    except Exception as e:
        print(f"   Error: {e}")
        sys.exit(1)

    # Send email
    print("\n4. Sending podcast via email...")
    if send_podcast_email(output_path, date):
        print("   Success!")
    else:
        print("   Failed to send email")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Podcast generation complete!")
    print("=" * 50)


if __name__ == '__main__':
    main()
