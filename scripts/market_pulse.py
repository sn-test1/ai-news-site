"""Generate Market Pulse data from the current article dataset."""

import json
import os
import re
from collections import Counter
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Company names to detect ────────────────────────────────────────────────────
COMPANIES = [
    "OpenAI", "Google", "Anthropic", "Meta", "Microsoft", "NVIDIA",
    "Amazon", "Apple", "Tesla", "IBM", "Samsung", "Intel", "AMD",
    "Hugging Face", "Mistral", "Stability AI", "Cohere", "xAI",
    "Perplexity", "Salesforce", "Adobe", "Oracle", "Baidu",
]

# ── Sentiment keywords ─────────────────────────────────────────────────────────
POSITIVE = {
    "breakthrough", "launch", "launches", "launched", "raise", "raises",
    "raised", "growth", "success", "advance", "improved", "improves",
    "improvement", "innovation", "record", "milestone", "partnership",
    "funding", "investment", "open-source", "upgrade", "expansion",
    "achievement", "accelerate", "boost", "surpass", "soar", "gain",
}

NEGATIVE = {
    "layoff", "layoffs", "cut", "cuts", "ban", "bans", "banned",
    "risk", "threat", "concern", "decline", "fail", "fails", "failed",
    "failure", "lawsuit", "hack", "breach", "vulnerability", "attack",
    "crash", "shutdown", "restrict", "restriction", "warning", "danger",
    "downturn", "loss", "losses", "penalty", "fine", "fined",
}

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "not", "no", "this", "that", "it",
    "its", "as", "than", "also", "new", "more", "about", "up", "out",
    "all", "their", "they", "which", "what", "how", "just", "now",
    "very", "one", "two", "first", "said", "says", "using", "used",
    "based", "across", "while", "including", "between", "after", "into",
    "before", "through", "under", "during", "per", "making", "made",
    "make", "some", "any", "most", "been", "over", "who", "where",
}


def load_articles():
    path = os.path.join(BASE_DIR, "data", "articles.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_previous_pulse():
    path = os.path.join(BASE_DIR, "data", "market_pulse.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_trending_topics(articles, top_n=3):
    """Top N trending keywords from titles and summaries."""
    word_counts = Counter()
    for a in articles:
        text = f"{a.get('title', '')} {a.get('summary', '')}"
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        for w in words:
            if w not in STOP_WORDS:
                word_counts[w] += 1
    return [word for word, _ in word_counts.most_common(top_n)]


def find_top_company(articles):
    """Most mentioned company across all article text."""
    counts = Counter()
    for a in articles:
        text = f"{a.get('title', '')} {a.get('summary', '')}".lower()
        for company in COMPANIES:
            if company.lower() in text:
                counts[company] += 1
    if not counts:
        return "N/A"
    return counts.most_common(1)[0][0]


def compute_sentiment(articles):
    """Overall sentiment from keyword frequency: positive, negative, or neutral."""
    pos = 0
    neg = 0
    for a in articles:
        text = f"{a.get('title', '')} {a.get('summary', '')}".lower()
        words = set(re.findall(r"\b[a-z]+\b", text))
        pos += len(words & POSITIVE)
        neg += len(words & NEGATIVE)
    if pos > neg * 1.3:
        return "Positive"
    elif neg > pos * 1.3:
        return "Negative"
    return "Neutral"


def count_new_articles(articles, previous_pulse):
    """Count articles not present in the previous run."""
    if not previous_pulse:
        return len(articles)
    prev_count = previous_pulse.get("total_articles", 0)
    return max(0, len(articles) - prev_count)


def generate_pulse():
    print("Generating Market Pulse...")

    articles = load_articles()
    previous = load_previous_pulse()

    trending = compute_trending_topics(articles)
    top_company = find_top_company(articles)
    sentiment = compute_sentiment(articles)
    new_articles = count_new_articles(articles, previous)
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    pulse = {
        "trending_topics": trending,
        "top_company": top_company,
        "sentiment": sentiment,
        "new_articles": new_articles,
        "total_articles": len(articles),
        "timestamp": timestamp,
    }

    # Save
    data_dir = os.path.join(BASE_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)
    out_path = os.path.join(data_dir, "market_pulse.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(pulse, f, indent=2, ensure_ascii=False)

    print(f"  Trending:      {', '.join(trending)}")
    print(f"  Top company:   {top_company}")
    print(f"  Sentiment:     {sentiment}")
    print(f"  New articles:  +{new_articles}")
    print(f"  Total:         {len(articles)}")
    print(f"  Saved to:      {out_path}")
    return pulse


if __name__ == "__main__":
    generate_pulse()
