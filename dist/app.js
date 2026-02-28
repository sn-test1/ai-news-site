/* ================================================================
   AI News Dashboard – Client Application
   ================================================================ */
(function () {
    'use strict';

    /* ── State ──────────────────────────────────────────────── */
    var articles      = window.ARTICLES_DATA || [];
    var selectedSources = {};
    var selectedTags    = {};
    var timeRange     = 'all';
    var searchQuery   = '';

    /* ── DOM refs ───────────────────────────────────────────── */
    var $grid           = document.getElementById('article-grid');
    var $noResults      = document.getElementById('no-results');
    var $feedCount      = document.getElementById('feed-count');
    var $searchInput    = document.getElementById('search-input');
    var $timeFilter     = document.getElementById('time-filter');
    var $darkToggle     = document.getElementById('dark-mode-toggle');
    var $filterToggle   = document.getElementById('filter-toggle');
    var $sidebar        = document.getElementById('sidebar');
    var $overlay        = document.getElementById('sidebar-overlay');
    var $clearFilters   = document.getElementById('clear-filters');

    /* ── Initialise ─────────────────────────────────────────── */
    function init() {
        loadTheme();
        renderArticles();
        bindEvents();
    }

    /* ── Render ─────────────────────────────────────────────── */
    function renderArticles() {
        var filtered = applyFilters();

        if (filtered.length === 0) {
            $grid.style.display = 'none';
            $noResults.style.display = 'block';
            $feedCount.textContent = '0 articles';
            return;
        }

        $grid.style.display = '';
        $noResults.style.display = 'none';
        $feedCount.textContent = filtered.length + ' article' + (filtered.length !== 1 ? 's' : '');

        var html = '';
        for (var i = 0; i < filtered.length; i++) {
            html += buildCard(filtered[i], i);
        }
        $grid.innerHTML = html;
    }

    function buildCard(article, index) {
        var delay = Math.min(index * 0.04, 0.6);
        var tags  = article.tags || [];
        var tagsHtml = '';
        for (var t = 0; t < tags.length; t++) {
            tagsHtml += '<span class="card-tag">' + esc(tags[t]) + '</span>';
        }
        return (
            '<article class="article-card" style="animation-delay:' + delay + 's">' +
                '<div class="card-header">' +
                    '<span class="source-badge" data-source="' + attr(article.source) + '">' + esc(article.source) + '</span>' +
                    '<time class="card-time" datetime="' + attr(article.published) + '">' + relTime(article.published) + '</time>' +
                '</div>' +
                '<h3 class="card-title"><a href="' + attr(article.link) + '" target="_blank" rel="noopener noreferrer">' + esc(article.title) + '</a></h3>' +
                '<p class="card-summary">' + esc(article.summary) + '</p>' +
                '<div class="card-footer">' +
                    tagsHtml +
                    '<a href="' + attr(article.link) + '" target="_blank" rel="noopener noreferrer" class="read-more">Read more &rarr;</a>' +
                '</div>' +
            '</article>'
        );
    }

    /* ── Filters ────────────────────────────────────────────── */
    function applyFilters() {
        var hasSources = Object.keys(selectedSources).length > 0;
        var hasTags    = Object.keys(selectedTags).length > 0;

        return articles.filter(function (a) {
            // Search
            if (searchQuery) {
                var q = searchQuery.toLowerCase();
                var hay = (a.title + ' ' + a.summary + ' ' + (a.tags || []).join(' ')).toLowerCase();
                if (hay.indexOf(q) === -1) return false;
            }
            // Source
            if (hasSources && !selectedSources[a.source]) return false;
            // Time range
            if (timeRange !== 'all') {
                var hours = (Date.now() - new Date(a.published).getTime()) / 3.6e6;
                var limits = { '24h': 24, '7d': 168, '30d': 720 };
                if (hours > (limits[timeRange] || Infinity)) return false;
            }
            // Tags
            if (hasTags) {
                var at = a.tags || [];
                var match = false;
                for (var i = 0; i < at.length; i++) {
                    if (selectedTags[at[i]]) { match = true; break; }
                }
                if (!match) return false;
            }
            return true;
        });
    }

    function clearAll() {
        searchQuery = '';
        $searchInput.value = '';
        selectedSources = {};
        selectedTags = {};
        timeRange = 'all';
        $timeFilter.value = 'all';
        var cbs = document.querySelectorAll('.source-filter');
        for (var i = 0; i < cbs.length; i++) cbs[i].checked = false;
        var tgs = document.querySelectorAll('.topic-tag');
        for (var j = 0; j < tgs.length; j++) tgs[j].classList.remove('active');
        renderArticles();
    }

    /* ── Theme ──────────────────────────────────────────────── */
    function loadTheme() {
        var saved = localStorage.getItem('ai-news-theme');
        var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        var theme = saved || (prefersDark ? 'dark' : 'light');
        document.documentElement.setAttribute('data-theme', theme);
    }

    function toggleTheme() {
        var cur = document.documentElement.getAttribute('data-theme');
        var next = cur === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('ai-news-theme', next);
    }

    /* ── Mobile sidebar ─────────────────────────────────────── */
    function openSidebar()  {
        $sidebar.classList.add('active');
        $overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    function closeSidebar() {
        $sidebar.classList.remove('active');
        $overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    /* ── Events ─────────────────────────────────────────────── */
    function bindEvents() {
        var debounce;
        $searchInput.addEventListener('input', function (e) {
            clearTimeout(debounce);
            debounce = setTimeout(function () {
                searchQuery = e.target.value.trim();
                renderArticles();
            }, 200);
        });

        var srcCbs = document.querySelectorAll('.source-filter');
        for (var s = 0; s < srcCbs.length; s++) {
            srcCbs[s].addEventListener('change', function () {
                if (this.checked) selectedSources[this.value] = true;
                else delete selectedSources[this.value];
                renderArticles();
            });
        }

        $timeFilter.addEventListener('change', function () {
            timeRange = this.value;
            renderArticles();
        });

        var tagBtns = document.querySelectorAll('.topic-tag');
        for (var t = 0; t < tagBtns.length; t++) {
            tagBtns[t].addEventListener('click', function () {
                var name = this.getAttribute('data-tag');
                if (selectedTags[name]) {
                    delete selectedTags[name];
                    this.classList.remove('active');
                } else {
                    selectedTags[name] = true;
                    this.classList.add('active');
                }
                renderArticles();
            });
        }

        $darkToggle.addEventListener('click', toggleTheme);

        if ($filterToggle) $filterToggle.addEventListener('click', openSidebar);
        if ($overlay)      $overlay.addEventListener('click', closeSidebar);
        if ($clearFilters) $clearFilters.addEventListener('click', clearAll);

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeSidebar();
            if (e.key === '/' && document.activeElement !== $searchInput) {
                e.preventDefault();
                $searchInput.focus();
            }
        });
    }

    /* ── Helpers ─────────────────────────────────────────────── */
    function relTime(iso) {
        var diff = Date.now() - new Date(iso).getTime();
        var m = Math.floor(diff / 6e4);
        var h = Math.floor(m / 60);
        var d = Math.floor(h / 24);
        if (d > 30) return new Date(iso).toLocaleDateString();
        if (d > 0)  return d + 'd ago';
        if (h > 0)  return h + 'h ago';
        if (m > 0)  return m + 'm ago';
        return 'Just now';
    }

    function esc(s) {
        if (!s) return '';
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(s));
        return d.innerHTML;
    }

    function attr(s) {
        if (!s) return '';
        return s.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }

    /* ── Boot ───────────────────────────────────────────────── */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
