"""Fetch AI news articles from public RSS feeds."""

import json
import os
import re
from datetime import datetime
from html import unescape
from time import mktime

import feedparser

# ── Feed sources ───────────────────────────────────────────────────────────────
FEEDS = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "MIT Technology Review": "https://www.technologyreview.com/feed/",
    "The Verge": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "VentureBeat": "https://venturebeat.com/category/ai/feed/",
}

# ── Tag keyword map ────────────────────────────────────────────────────────────
TAG_KEYWORDS = {
    "LLM": ["llm", "language model", "gpt", "chatgpt", "gemini", "claude", "llama"],
    "OpenAI": ["openai", "gpt-4", "gpt-5", "chatgpt", "dall-e"],
    "Google": ["google", "deepmind", "gemini", "bard"],
    "Anthropic": ["anthropic", "claude"],
    "Regulation": ["regulation", "regulatory", "policy", "governance", "eu ai act"],
    "Healthcare": ["health", "medical", "clinical", "drug", "diagnosis", "cancer"],
    "Robotics": ["robot", "robotics", "autonomous", "humanoid"],
    "Hardware": ["chip", "gpu", "nvidia", "semiconductor", "tpu", "accelerator"],
    "AI Safety": ["safety", "alignment", "bias", "ethical", "responsible ai"],
    "Open Source": ["open source", "open-source", "hugging face", "huggingface"],
    "Research": ["research", "study", "paper", "arxiv", "breakthrough"],
    "Enterprise": ["enterprise", "business", "saas", "productivity", "copilot"],
    "Funding": ["funding", "investment", "raised", "valuation", "series"],
    "Coding": ["code", "coding", "programming", "developer", "software engineer"],
}

MAX_ARTICLES_PER_FEED = 15


def strip_html(text):
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_tags(title, summary):
    """Extract topic tags based on keyword matching."""
    text = f"{title} {summary}".lower()
    tags = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    return tags[:5]


def parse_date(entry):
    """Extract and normalize publication date from a feed entry."""
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                dt = datetime.fromtimestamp(mktime(parsed))
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except (ValueError, OverflowError):
                pass
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_articles():
    """Fetch articles from all configured RSS feeds."""
    articles = []

    for source, url in FEEDS.items():
        print(f"Fetching: {source} ...")
        try:
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                print(f"  Warning: could not parse {source}")
                continue

            count = 0
            for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                raw_summary = entry.get("summary", entry.get("description", ""))
                summary = strip_html(raw_summary)[:300]
                published = parse_date(entry)

                if not title or not link:
                    continue

                tags = extract_tags(title, summary)

                articles.append({
                    "title": title,
                    "link": link,
                    "source": source,
                    "published": published,
                    "summary": summary,
                    "tags": tags,
                })
                count += 1

            print(f"  Got {count} articles")
        except Exception as e:
            print(f"  Error: {e}")

    if not articles:
        print("\nNo articles fetched. Keeping existing data/articles.json.")
        return []

    # Sort newest first
    articles.sort(key=lambda a: a["published"], reverse=True)

    # Save
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, "articles.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(articles)} articles to {output_path}")
    return articles


if __name__ == "__main__":
    fetch_articles()
