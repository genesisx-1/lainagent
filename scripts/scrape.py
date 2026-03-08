#!/usr/bin/env python3
"""Web scraper for Agent Office CRM"""
import requests
from bs4 import BeautifulSoup
import json
import sys
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'crm.db')

def scrape_url(url):
    """Scrape a URL and return structured data"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AgentOffice/1.0'}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Remove scripts and styles
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        title = soup.title.string.strip() if soup.title else ''

        # Extract text content
        text = soup.get_text(separator='\n', strip=True)
        # Limit text
        text = text[:5000]

        # Extract links
        links = []
        for a in soup.find_all('a', href=True)[:20]:
            href = a['href']
            if href.startswith('http'):
                links.append({'url': href, 'text': a.get_text(strip=True)[:80]})

        # Extract emails
        import re
        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resp.text)))[:10]

        # Extract phone numbers
        phones = list(set(re.findall(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}', resp.text)))[:10]

        # Meta description
        meta_desc = ''
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            meta_desc = meta.get('content', '')

        return {
            'url': url,
            'title': title,
            'description': meta_desc,
            'content': text[:3000],
            'links': links,
            'emails': emails,
            'phones': phones,
            'status': 'done',
        }
    except Exception as e:
        return {'url': url, 'status': 'error', 'error': str(e)}

def save_to_db(result):
    """Save scrape result to the CRM database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE scrape_results SET title=?, content=?, data=?, status=? WHERE url=? AND status='pending'",
            (result.get('title',''), result.get('content','')[:3000],
             json.dumps({k:v for k,v in result.items() if k not in ('content',)}),
             result.get('status','done'), result['url'])
        )
        if conn.total_changes == 0:
            conn.execute(
                "INSERT INTO scrape_results (url, title, content, data, status) VALUES (?,?,?,?,?)",
                (result['url'], result.get('title',''), result.get('content','')[:3000],
                 json.dumps({k:v for k,v in result.items() if k not in ('content',)}),
                 result.get('status','done'))
            )
        # Auto-create contacts from found emails
        for email in result.get('emails', []):
            name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            conn.execute(
                "INSERT OR IGNORE INTO contacts (name, email, source, notes) VALUES (?, ?, 'scraped', ?)",
                (name, email, f"Found on {result['url']}")
            )
        conn.commit()
        conn.close()
    except Exception as e:
        print(json.dumps({"error": f"DB save failed: {e}"}), file=sys.stderr)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: scrape.py <url>"}))
        sys.exit(1)

    url = sys.argv[1]
    result = scrape_url(url)
    save_to_db(result)
    print(json.dumps(result, indent=2))
