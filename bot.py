"""
Discord News Bot — Taggart Institute Intel Center RSS Monitor
Polls the RSS feed, filters to today's articles, and sends new ones to Discord.
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
RSS_FEED_URL = "https://news.ifin.network/i/?a=rss"
SEEN_FILE = Path(__file__).parent / "seen_articles.json"


def load_seen() -> set[str]:
    """
    Load the set of seen article GUIDs from the JSON file.
    """
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text()))
        except (json.JSONDecodeError, TypeError):
            pass
    return set()


def save_seen(seen: set[str]) -> None:
    """
    Save the set of seen article GUIDs to the JSON file.
    """
    SEEN_FILE.write_text(json.dumps(list(seen), indent=2))


def strip_html(text: str) -> str:
    """
    Remove HTML tags and unescape common entities from a string.
    """
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", text).strip()


def is_today(entry) -> bool:
    """
    Check if an RSS entry was published today (UTC).
    """
    parsed = entry.get("published_parsed")
    if not parsed:
        return False
    pub_date = datetime(*parsed[:6], tzinfo=timezone.utc).date()
    return pub_date == datetime.now(timezone.utc).date()


def fetch_todays_articles() -> list[dict]:
    """
    Fetch RSS feed and return only today's articles, oldest first.
    """
    print("Fetching feed…")
    feed = feedparser.parse(RSS_FEED_URL)

    articles = []
    for entry in feed.entries:
        if not is_today(entry):
            continue

        summary = strip_html(entry.get("summary", ""))
        if len(summary) > 300:
            summary = summary[:297] + "…"

        articles.append(
            {
                "guid": entry.get("id") or entry.get("link", ""),
                "title": entry.get("title", "No title"),
                "link": entry.get("link", ""),
                "author": entry.get("dc_creator") or entry.get("author", "Unknown"),
                "summary": summary,
            }
        )

    articles.reverse()  # oldest first
    return articles


def send_to_discord(article: dict) -> bool:
    """
    Send an article to the Discord webhook.
    """
    payload = {
        "username": "TTI Intel Bot",
        "embeds": [
            {
                "title": article["title"],
                "url": article["link"],
                "description": article["summary"] or "No summary available.",
                "color": 0x00B4D8,
                "footer": {"text": f"Source: {article['author']}"},
            }
        ],
    }

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=15)
        if resp.status_code == 204:
            print(f"✅  Sent: {article['title']}")
            return True
        if resp.status_code == 429:
            retry_after = resp.json().get("retry_after", 5)
            print(f"Rate-limited — retrying in {retry_after}s")
            time.sleep(retry_after)
            return send_to_discord(article)
        print(f"Discord error {resp.status_code}: {resp.text}")
    except requests.RequestException as exc:
        print(f"Request failed: {exc}")
    return False


def run() -> None:
    """
    Fetch today's articles and send new ones to Discord.
    """
    if not DISCORD_WEBHOOK_URL:
        print("❌  Set DISCORD_WEBHOOK_URL in your .env file.")
        return

    print("🚀  Checking for new articles…")
    seen = load_seen()

    articles = fetch_todays_articles()
    new_count = 0

    for article in articles:
        if article["guid"] in seen:
            continue

        seen.add(article["guid"])
        send_to_discord(article)
        new_count += 1
        time.sleep(1)

    save_seen(seen)
    print(f"📬  {new_count} new article(s)" if new_count else "📭  No new articles.")


if __name__ == "__main__":
    run()
