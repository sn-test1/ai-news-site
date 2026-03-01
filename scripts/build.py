"""Build the static AI News Dashboard from template + data."""

import json
import os
import re
import shutil
from collections import Counter
from datetime import datetime

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "not", "no", "this",
    "that", "these", "those", "it", "its", "as", "than", "also", "new",
    "more", "about", "up", "out", "into", "all", "their", "they", "which",
    "what", "when", "where", "who", "how", "each", "other", "over", "such",
    "most", "some", "any", "just", "now", "very", "one", "two", "first",
    "said", "says", "using", "used", "based", "across", "while", "including",
    "between", "after", "before", "through", "under", "during", "per",
    "its", "has", "been", "can", "will", "making", "made", "make",
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_articles():
    """Load articles from data/articles.json."""
    path = os.path.join(BASE_DIR, "data", "articles.json")
    if not os.path.exists(path):
        print("Warning: data/articles.json not found. Using empty dataset.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_trending(articles, top_n=8):
    """Compute trending keywords from article titles and summaries."""
    word_counts = Counter()
    for article in articles:
        text = f"{article.get('title', '')} {article.get('summary', '')}"
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        for word in words:
            if word not in STOP_WORDS:
                word_counts[word] += 1
    return word_counts.most_common(top_n)


def generate_summary(articles):
    """Generate a human-readable update summary."""
    count = len(articles)
    sources = set(a.get("source", "Unknown") for a in articles)
    all_tags = []
    for a in articles:
        all_tags.extend(a.get("tags", []))
    top_tags = [tag for tag, _ in Counter(all_tags).most_common(3)]

    if count == 0:
        return "No articles available. Run the fetch script to pull the latest AI news."

    tag_str = ", ".join(top_tags) if top_tags else "various AI topics"
    return (
        f"Tracking {count} articles from {len(sources)} sources. "
        f"Latest coverage spans {tag_str}, and more."
    )


def get_all_tags(articles):
    """Get all unique tags sorted by frequency."""
    tag_counts = Counter()
    for a in articles:
        for tag in a.get("tags", []):
            tag_counts[tag] += 1
    return tag_counts.most_common()


def get_source_counts(articles):
    """Get sources with article counts."""
    source_counts = Counter()
    for a in articles:
        source_counts[a.get("source", "Unknown")] += 1
    return source_counts.most_common()


def load_market_pulse():
    """Load market pulse data from data/market_pulse.json."""
    path = os.path.join(BASE_DIR, "data", "market_pulse.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── HTML generators ────────────────────────────────────────────────────────────

def build_market_pulse_html(pulse):
    """Generate the Market Pulse panel HTML."""
    if not pulse:
        return '<p class="pulse-empty">Market Pulse data not yet available.</p>'

    trending = pulse.get("trending_topics", [])
    top_company = pulse.get("top_company", "N/A")
    sentiment = pulse.get("sentiment", "Neutral")
    new_articles = pulse.get("new_articles", 0)
    timestamp = pulse.get("timestamp", "")

    # Format timestamp for display
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        ts_display = dt.strftime("%b %d, %Y at %H:%M UTC")
    except (ValueError, TypeError):
        ts_display = timestamp

    # Sentiment indicator
    sentiment_icons = {"Positive": "\u25b2", "Negative": "\u25bc", "Neutral": "\u25c6"}
    sentiment_classes = {"Positive": "positive", "Negative": "negative", "Neutral": "neutral"}
    s_icon = sentiment_icons.get(sentiment, "\u25c6")
    s_class = sentiment_classes.get(sentiment, "neutral")

    # Trending topics list
    trending_items = ""
    for i, topic in enumerate(trending, 1):
        trending_items += f'<span class="pulse-topic">#{i} {topic}</span>'

    return (
        f'<div class="pulse-grid">'
        f'<div class="pulse-card">'
        f'<span class="pulse-card-label">Trending Topics</span>'
        f'<div class="pulse-topics">{trending_items}</div>'
        f'</div>'
        f'<div class="pulse-card">'
        f'<span class="pulse-card-label">Top Company</span>'
        f'<span class="pulse-card-value">{top_company}</span>'
        f'</div>'
        f'<div class="pulse-card">'
        f'<span class="pulse-card-label">Sentiment</span>'
        f'<span class="pulse-card-value pulse-sentiment {s_class}">{s_icon} {sentiment}</span>'
        f'</div>'
        f'<div class="pulse-card">'
        f'<span class="pulse-card-label">New Articles</span>'
        f'<span class="pulse-card-value pulse-new">+{new_articles}</span>'
        f'</div>'
        f'<div class="pulse-card">'
        f'<span class="pulse-card-label">Updated</span>'
        f'<span class="pulse-card-value pulse-time">{ts_display}</span>'
        f'</div>'
        f'</div>'
    )


def build_source_filters_html(source_counts):
    html = ""
    for source, count in source_counts:
        safe = source.replace('"', "&quot;")
        html += (
            f'<label class="filter-checkbox">'
            f'<input type="checkbox" class="source-filter" value="{safe}">'
            f'<span class="checkbox-custom"></span>'
            f'<span class="checkbox-label">{source}</span>'
            f'<span class="filter-count">{count}</span>'
            f"</label>\n"
        )
    return html


def build_topic_tags_html(tag_counts):
    html = ""
    for tag, count in tag_counts:
        safe = tag.replace('"', "&quot;")
        html += (
            f'<button class="topic-tag" data-tag="{safe}">'
            f'{tag} <span class="tag-count">{count}</span></button>\n'
        )
    return html


def build_trending_html(trending):
    if not trending:
        return '<p class="trending-empty">No trending data available.</p>'
    max_count = trending[0][1]
    html = ""
    for i, (word, count) in enumerate(trending, 1):
        pct = int((count / max_count) * 100)
        html += (
            f'<div class="trending-item">'
            f'<div class="trending-bar" style="width: {pct}%"></div>'
            f'<span class="trending-rank">#{i}</span>'
            f'<span class="trending-word">{word}</span>'
            f'<span class="trending-count">{count}</span>'
            f"</div>\n"
        )
    return html


# ── Main build ─────────────────────────────────────────────────────────────────

def build():
    print("Building AI News Dashboard...")

    articles = load_articles()
    pulse = load_market_pulse()
    trending = compute_trending(articles)
    summary = generate_summary(articles)
    last_updated = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
    source_counts = get_source_counts(articles)
    tag_counts = get_all_tags(articles)

    # Read HTML template
    template_path = os.path.join(BASE_DIR, "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Encode articles as JSON safe for <script> embedding
    articles_json = json.dumps(articles, ensure_ascii=False).replace("</", "<\\/")

    # Replace template placeholders
    replacements = {
        "{{LAST_UPDATED}}": last_updated,
        "{{UPDATE_SUMMARY}}": summary,
        "{{ARTICLE_COUNT}}": str(len(articles)),
        "{{SOURCE_COUNT}}": str(len(source_counts)),
        "{{SOURCE_FILTERS}}": build_source_filters_html(source_counts),
        "{{TOPIC_TAGS}}": build_topic_tags_html(tag_counts),
        "{{TRENDING_TOPICS}}": build_trending_html(trending),
        "{{MARKET_PULSE}}": build_market_pulse_html(pulse),
        "{{ARTICLES_JSON}}": articles_json,
    }

    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    # Write to dist/
    dist_dir = os.path.join(BASE_DIR, "dist")
    os.makedirs(dist_dir, exist_ok=True)

    with open(os.path.join(dist_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    # Copy static assets
    static_dir = os.path.join(BASE_DIR, "static")
    for filename in ("style.css", "app.js"):
        src = os.path.join(static_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dist_dir, filename))

    print(f"Done! Output in: {dist_dir}")
    print(f"  Articles: {len(articles)}")
    print(f"  Sources:  {len(source_counts)}")
    print(f"  Trending: {len(trending)} topics")
    print(f"\nOpen dist/index.html in your browser to preview.")


if __name__ == "__main__":
    build()
