#!/usr/bin/env bash
# Automated AI News Dashboard update script.
# Fetches latest articles, rebuilds the site, and pushes changes if any.

set -euo pipefail

REPO_DIR="/workspace/ai-news-site"

echo "$(date -u '+%Y-%m-%d %H:%M:%S UTC') — Starting AI News Dashboard update..."

# Fetch latest articles
python3 "$REPO_DIR/scripts/fetch_feeds.py"

# Rebuild the site
python3 "$REPO_DIR/scripts/build.py"

# Commit and push if there are changes
cd "$REPO_DIR"
if git diff --quiet data/articles.json dist/index.html 2>/dev/null; then
    echo "No changes detected. Skipping commit."
else
    git add data/articles.json dist/index.html
    ARTICLE_COUNT=$(python3 -c "import json; print(len(json.load(open('data/articles.json'))))")
    TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M UTC')
    git commit -m "Auto-update dashboard: ${ARTICLE_COUNT} articles (${TIMESTAMP})

Co-Authored-By: Oz <oz-agent@warp.dev>"
    git push origin master
    echo "Changes committed and pushed."
fi

echo "$(date -u '+%Y-%m-%d %H:%M:%S UTC') — Update complete."
