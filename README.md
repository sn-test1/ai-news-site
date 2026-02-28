# AI News Dashboard

A static site that aggregates AI-related news from public RSS feeds and presents them in a modern, interactive dashboard.

## Features

- Pulls articles from multiple AI / tech RSS feeds
- Clean card-based layout with source badges and relative timestamps
- Full-text search across titles, summaries, and tags
- Sidebar filters: source, time range, and topic tags
- Trending Topics section computed from keyword frequency
- Dark mode with system-preference detection and toggle
- Fully responsive — mobile sidebar slides in from the left
- Keyboard shortcuts: `/` to focus search, `Esc` to close sidebar

## Quick Start

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Fetch articles (optional — sample data is included)

```
python scripts/fetch_feeds.py
```

### 3. Build the site

```
python scripts/build.py
```

### 4. Open the dashboard

Open `dist/index.html` in your browser.

## Project Structure

```
ai-news-site/
├── data/
│   └── articles.json        # Article data (sample included)
├── scripts/
│   ├── fetch_feeds.py        # RSS feed fetcher
│   └── build.py              # Static site builder
├── templates/
│   └── index.html            # HTML template with placeholders
├── static/
│   ├── style.css             # Stylesheet
│   └── app.js                # Client-side JavaScript
├── dist/                     # Built output (generated)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt
└── README.md
```

## Build Pipeline

1. **fetch_feeds.py** — fetches RSS feeds → writes `data/articles.json`
2. **build.py** — reads article data → computes `last_updated`, `trending_topics`, `update_summary` → injects values into the HTML template → copies assets to `dist/`

## RSS Feeds

Default sources (edit `FEEDS` in `scripts/fetch_feeds.py` to customise):

- TechCrunch (AI category)
- MIT Technology Review
- The Verge (AI section)
- Ars Technica (Technology Lab)
- VentureBeat (AI category)
