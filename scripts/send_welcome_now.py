#!/usr/bin/env python3
"""
Send welcome emails to new recipients.
Run this after domain verification is complete.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Load environment
PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from dotenv import load_dotenv
load_dotenv(PROJECT_DIR / '.env.local')

import requests

RESEND_API_KEY = os.getenv('RESEND_API_KEY')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

NEW_RECIPIENTS = [
    "adam.sadowski@acrartex.com",
    "jim.story@acrartex.com",
    "chris.bolender@acrartex.com"
]

def get_latest_digest():
    """Fetch the latest digest from Supabase"""
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    result = supabase.table('digests').select('*').order('date', desc=True).limit(1).execute()
    return result.data[0] if result.data else None

def generate_welcome_html(digest):
    """Generate welcome email HTML"""
    date = digest['date']
    content = digest['content']

    formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%A, %B %d, %Y')

    def format_item(item):
        topics = ''.join([f'<span style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-right: 4px;">{t}</span>' for t in item.get('topics', [])])
        return f'''
        <tr>
          <td style="padding: 12px 0; border-bottom: 1px solid #eee;">
            <a href="{item['url']}" style="color: #1a1a1a; text-decoration: none; font-weight: 600; font-size: 15px;">
              {item['title']}
            </a>
            <p style="margin: 4px 0 0 0; color: #666; font-size: 13px; line-height: 1.4;">
              {item['summary']}
            </p>
            <p style="margin: 4px 0 0 0; color: #0066cc; font-size: 12px;">
              {item['why_it_matters']}
            </p>
            <p style="margin: 4px 0 0 0;">{topics}</p>
          </td>
        </tr>
        '''

    def format_section(title, emoji, items):
        if not items:
            return ''
        return f'''
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px;">
          <tr>
            <td style="padding-bottom: 8px; border-bottom: 2px solid #1a1a1a;">
              <h2 style="margin: 0; font-size: 18px; color: #1a1a1a;">{emoji} {title}</h2>
            </td>
          </tr>
          {''.join([format_item(item) for item in items])}
        </table>
        '''

    welcome_message = '''
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px;">
      <tr>
        <td style="padding: 30px; color: white;">
          <h2 style="margin: 0 0 15px 0; font-size: 22px;">Welcome to the AI News Agent!</h2>
          <p style="margin: 0 0 15px 0; font-size: 15px; line-height: 1.6;">
            This system was <strong>built from scratch by Chris</strong> to keep you informed on the rapidly evolving AI landscape.
          </p>
          <p style="margin: 0 0 15px 0; font-size: 15px; line-height: 1.6;">
            <strong>Why daily updates matter:</strong> AI is advancing at a pace that makes Moore's Law look slow.
            While Moore's Law predicted computing power doubling every 2 years, AI capabilities are now
            <strong>doubling every 6 months</strong>. NVIDIA's CEO Jensen Huang calls it "Moore's Law squared" —
            AI has advanced <strong>100,000x in a decade</strong>, compared to the 100x that Moore's Law would predict.
          </p>
          <p style="margin: 0 0 15px 0; font-size: 15px; line-height: 1.6;">
            With $320+ billion in AI infrastructure spending in 2025 alone and breakthroughs happening weekly,
            staying current isn't optional — it's essential.
          </p>
          <div style="background: rgba(255,255,255,0.15); border-radius: 8px; padding: 15px; margin-top: 20px;">
            <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold;">Your Daily Briefing:</p>
            <p style="margin: 0; font-size: 14px;">
              📬 <strong>Email Digest + Audio Podcast</strong> delivered at <strong>4:30 PM ET</strong> every day
            </p>
          </div>
        </td>
      </tr>
    </table>
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 25px; background: #f8f9fa; border-radius: 8px;">
      <tr>
        <td style="padding: 20px;">
          <h3 style="margin: 0 0 12px 0; font-size: 16px; color: #1a1a1a;">What Makes This Unique: 22 Diverse Sources</h3>
          <table width="100%" cellpadding="0" cellspacing="0" style="font-size: 13px; color: #444;">
            <tr>
              <td style="padding: 4px 0; vertical-align: top; width: 50%;">
                <strong>Research:</strong><br/>arXiv (ML, AI, NLP, CV, Robotics), HuggingFace Papers
              </td>
              <td style="padding: 4px 0; vertical-align: top;">
                <strong>Lab Blogs:</strong><br/>OpenAI, DeepMind, Google Research, Meta AI, Microsoft Research
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0 4px 0; vertical-align: top;">
                <strong>Enterprise:</strong><br/>VentureBeat, Ars Technica, AWS ML, NVIDIA, MLOps Community
              </td>
              <td style="padding: 8px 0 4px 0; vertical-align: top;">
                <strong>Community:</strong><br/>r/MachineLearning, r/LocalLLaMA, Hacker News
              </td>
            </tr>
            <tr>
              <td colspan="2" style="padding: 8px 0 0 0; vertical-align: top;">
                <strong>Robotics & Industrial:</strong> Robot Report, Robohub, Roboflow, Automation World
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    '''

    return f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #fff;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td style="padding-bottom: 20px; border-bottom: 3px solid #1a1a1a;">
        <h1 style="margin: 0; font-size: 24px; color: #1a1a1a;">AI News Digest</h1>
        <p style="margin: 4px 0 0 0; color: #666; font-size: 14px;">{formatted_date}</p>
      </td>
    </tr>
    <tr>
      <td style="padding-top: 20px;">
        {welcome_message}
        {format_section('Must Know', '🔴', content.get('must_know', []))}
        {format_section('Worth a Look', '🟡', content.get('worth_a_look', []))}
        {format_section('Quick Hits', '🔵', content.get('quick_hits', []))}
      </td>
    </tr>
    <tr>
      <td style="padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 12px;">
        <p>Generated by AI News Agent (Built by Chris)</p>
      </td>
    </tr>
  </table>
</body>
</html>'''

def send_welcome_emails(from_email="AI News Agent <news@acrartex.com>"):
    """Send welcome emails to new recipients"""
    digest = get_latest_digest()
    if not digest:
        print("No digest found!")
        return False

    html_content = generate_welcome_html(digest)

    # Send via Resend
    response = requests.post(
        'https://api.resend.com/emails',
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'from': from_email,
            'to': NEW_RECIPIENTS,
            'subject': f"Welcome to AI News Digest — Your First Briefing ({digest['date']})",
            'html': html_content
        }
    )

    if response.status_code == 200:
        print(f"✓ Welcome emails sent successfully to: {', '.join(NEW_RECIPIENTS)}")
        return True
    else:
        print(f"✗ Failed to send: {response.text}")
        return False

def save_welcome_html():
    """Save welcome email as HTML file for manual sending"""
    digest = get_latest_digest()
    if not digest:
        print("No digest found!")
        return

    html_content = generate_welcome_html(digest)
    output_path = PROJECT_DIR / 'welcome_emails' / f"welcome_{digest['date']}.html"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(html_content)
    print(f"✓ Welcome email saved to: {output_path}")
    return output_path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--send', action='store_true', help='Send emails (requires verified domain)')
    parser.add_argument('--save', action='store_true', help='Save HTML file for manual sending')
    args = parser.parse_args()

    if args.send:
        send_welcome_emails()
    elif args.save:
        save_welcome_html()
    else:
        print("Usage: python send_welcome_now.py --send (or --save)")
        print("\nRecipients:", NEW_RECIPIENTS)
