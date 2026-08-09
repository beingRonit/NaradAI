"""
High-Performance RSS News Collector

Responsibilities:

    RSS feeds
        ↓
    Parallel fetching
        ↓
    Conditional HTTP requests
        ↓
    RSS parsing
        ↓
    HTML cleanup
        ↓
    Topic normalization
        ↓
    Filtering
        ↓
    Deduplication
        ↓
    Topic[]

This collector intentionally does NOT perform:
    - deep verification
    - LLM evaluation
    - ranking
    - publishing
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import re
import threading

try:
    import feedparser
except ImportError:  # optional dependency; XML fallback below
    feedparser = None
import requests
import xml.etree.ElementTree as ET

from app.agent.models import Topic


# ==========================================================
# HTML CLEANER
# ==========================================================

class HTMLTextExtractor(HTMLParser):
    """
    Converts HTML into plain text.
    """

    def __init__(self):
        super().__init__()

        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def get_text(self):
        return " ".join(
            self.parts
        )


# ==========================================================
# NEWS COLLECTOR
# ==========================================================

class NewsCollector:
    """
    Collects and normalizes RSS news feeds.
    """

    # ==========================================================
    # RSS SOURCES
    # ==========================================================

    RSS_FEEDS = {
        "TechCrunch AI":
            "https://techcrunch.com/category/artificial-intelligence/feed/",

        "The Verge AI":
            "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",

        "Ars Technica":
            "https://feeds.arstechnica.com/arstechnica/index",
    }

    # ==========================================================
    # CONFIGURATION
    # ==========================================================

    MAX_WORKERS = 3

    MAX_ARTICLES_PER_FEED = 20

    REQUEST_TIMEOUT = 10

    USER_AGENT = (
        "AutonomousAI-NewsCollector/1.0 "
        "(Hackathon project; RSS reader)"
    )

    # Only collect articles newer than this many days.

    MAX_ARTICLE_AGE_DAYS = 3

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self):

        self.last_collection_time = None

        self.last_errors = []

        self.total_collected = 0

        self.total_before_deduplication = 0

        self.feed_statistics = {}

        # Conditional HTTP request cache.

        self._feed_cache = {}

        # Thread safety.

        self._cache_lock = threading.Lock()

        # HTTP session.

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": self.USER_AGENT,
                "Accept": (
                    "application/rss+xml, "
                    "application/atom+xml, "
                    "application/xml, "
                    "text/xml, "
                    "*/*;q=0.8"
                ),
            }
        )

    # ==========================================================
    # MAIN COLLECTION
    # ==========================================================

    def collect(self) -> list[Topic]:
        """
        Collect articles from all RSS feeds in parallel.
        """

        self.last_collection_time = datetime.now(
            timezone.utc
        )

        self.last_errors = []

        self.feed_statistics = {}

        all_topics = []

        # ------------------------------------------------------
        # PARALLEL FEED FETCHING
        # ------------------------------------------------------

        with ThreadPoolExecutor(
            max_workers=self.MAX_WORKERS
        ) as executor:

            futures = {
                executor.submit(
                    self._collect_feed,
                    source_name,
                    feed_url
                ): source_name

                for source_name, feed_url
                in self.RSS_FEEDS.items()
            }

            for future in as_completed(futures):

                source_name = futures[future]

                try:

                    topics = future.result()

                    all_topics.extend(
                        topics
                    )

                except Exception as error:

                    self.last_errors.append(
                        {
                            "source": source_name,
                            "error": str(error)
                        }
                    )

        # ------------------------------------------------------
        # FILTER
        # ------------------------------------------------------

        filtered_topics = self._filter_topics(
            all_topics
        )

        # ------------------------------------------------------
        # DEDUPLICATION
        # ------------------------------------------------------

        self.total_before_deduplication = len(
            filtered_topics
        )

        unique_topics = self._deduplicate(
            filtered_topics
        )

        self.total_collected = len(
            unique_topics
        )

        return unique_topics

    # ==========================================================
    # COLLECT ONE FEED
    # ==========================================================

    def _collect_feed(
        self,
        source_name: str,
        feed_url: str
    ) -> list[Topic]:
        """
        Fetch and parse one RSS feed.
        """

        response = self._fetch_feed(
            source_name,
            feed_url
        )

        # ------------------------------------------------------
        # HTTP 304
        # ------------------------------------------------------

        if response is None:

            self.feed_statistics[
                source_name
            ] = {
                "status": "NOT_MODIFIED",
                "articles": 0
            }

            return []

        # ------------------------------------------------------
        # PARSE RSS
        # ------------------------------------------------------

        parsed_feed = feedparser.parse(
            response.content
        )

        # ------------------------------------------------------
        # FEED ERROR
        # ------------------------------------------------------

        if parsed_feed.bozo:

            exception = getattr(
                parsed_feed,
                "bozo_exception",
                None
            )

            self.last_errors.append(
                {
                    "source": source_name,
                    "error": str(exception)
                }
            )

        # ------------------------------------------------------
        # ARTICLES
        # ------------------------------------------------------

        topics = []

        entries = parsed_feed.entries[
            :self.MAX_ARTICLES_PER_FEED
        ]

        for entry in entries:

            try:

                topic = self._entry_to_topic(
                    source_name,
                    entry
                )

                if topic is not None:

                    topics.append(
                        topic
                    )

            except Exception as error:

                self.last_errors.append(
                    {
                        "source": source_name,
                        "error": (
                            f"Article parsing error: "
                            f"{error}"
                        )
                    }
                )

        self.feed_statistics[
            source_name
        ] = {
            "status": "OK",
            "articles": len(topics)
        }

        return topics

    # ==========================================================
    # HTTP FETCH
    # ==========================================================

    def _fetch_feed(
        self,
        source_name: str,
        feed_url: str
    ):
        """
        Fetch RSS feed with conditional HTTP support.

        Uses ETag / Last-Modified when available.
        """

        headers = {}

        # ------------------------------------------------------
        # LOAD PREVIOUS CACHE
        # ------------------------------------------------------

        with self._cache_lock:

            cached = self._feed_cache.get(
                feed_url,
                {}
            )

        if cached.get("etag"):

            headers["If-None-Match"] = (
                cached["etag"]
            )

        if cached.get("last_modified"):

            headers["If-Modified-Since"] = (
                cached["last_modified"]
            )

        # ------------------------------------------------------
        # REQUEST
        # ------------------------------------------------------

        response = self.session.get(
            feed_url,
            headers=headers,
            timeout=self.REQUEST_TIMEOUT
        )

        # ------------------------------------------------------
        # NOT MODIFIED
        # ------------------------------------------------------

        if response.status_code == 304:

            return None

        # ------------------------------------------------------
        # HTTP ERROR
        # ------------------------------------------------------

        response.raise_for_status()

        # ------------------------------------------------------
        # UPDATE CACHE
        # ------------------------------------------------------

        with self._cache_lock:

            self._feed_cache[
                feed_url
            ] = {
                "etag": response.headers.get(
                    "ETag"
                ),

                "last_modified":
                    response.headers.get(
                        "Last-Modified"
                    )
            }

        return response

    # ==========================================================
    # ENTRY → TOPIC
    # ==========================================================

    def _parse_rss_xml(self, content):
        """Small RSS/Atom fallback when feedparser is unavailable."""
        root = ET.fromstring(content)
        entries = []
        # RSS 2.0
        for item in root.findall(".//item"):
            entries.append({
                "title": item.findtext("title", ""),
                "link": item.findtext("link", ""),
                "description": item.findtext("description", ""),
                "summary": item.findtext("description", ""),
                "published": item.findtext("pubDate", ""),
                "author": item.findtext("author", ""),
            })
        # Atom
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for entry in root.findall(".//a:entry", ns):
            link = entry.find("a:link", ns)
            entries.append({
                "title": entry.findtext("a:title", "", ns),
                "link": link.attrib.get("href", "") if link is not None else "",
                "description": entry.findtext("a:summary", "", ns),
                "summary": entry.findtext("a:summary", "", ns),
                "published": entry.findtext("a:published", "", ns) or entry.findtext("a:updated", "", ns),
                "author": entry.findtext("a:author/a:name", "", ns),
            })
        return type("ParsedFeed", (), {"entries": entries})()

    def _entry_to_topic(
        self,
        source_name: str,
        entry
    ) -> Topic | None:
        """
        Convert an RSS entry into a Topic.
        """

        title = self._clean_text(
            getattr(
                entry,
                "title",
                ""
            )
        )

        url = (
            getattr(
                entry,
                "link",
                ""
            )
            or ""
        ).strip()

        if not title or not url:

            return None

        # ------------------------------------------------------
        # SUMMARY
        # ------------------------------------------------------

        summary = self._clean_text(
            getattr(
                entry,
                "summary",
                ""
            )
        )

        # Some feeds use description.

        if not summary:

            summary = self._clean_text(
                getattr(
                    entry,
                    "description",
                    ""
                )
            )

        # ------------------------------------------------------
        # AUTHOR
        # ------------------------------------------------------

        author = self._clean_text(
            getattr(
                entry,
                "author",
                ""
            )
        )

        # ------------------------------------------------------
        # DATE
        # ------------------------------------------------------

        published_at = (
            self._get_published_time(
                entry
            )
        )

        # ------------------------------------------------------
        # CATEGORY
        # ------------------------------------------------------

        category = self._detect_category(
            title,
            summary,
            source_name
        )

        # ------------------------------------------------------
        # TAGS
        # ------------------------------------------------------

        tags = self._generate_tags(
            title,
            summary
        )

        # ------------------------------------------------------
        # ID
        # ------------------------------------------------------

        topic_id = self._generate_topic_id(
            url
        )

        # ------------------------------------------------------
        # IMAGE
        # ------------------------------------------------------

        image_url = self._get_image_url(
            entry
        )

        return Topic(
            id=topic_id,

            url=url,

            title=title,

            summary=summary,

            content=summary,

            source=source_name,

            author=author,

            category=category,

            language="en",

            tags=tags,

            image_url=image_url,

            published_at=published_at,

            discovered_at=datetime.now(
                timezone.utc
            )
        )

    # ==========================================================
    # CLEAN HTML
    # ==========================================================

    def _clean_text(
        self,
        text: str
    ) -> str:
        """
        Convert RSS HTML content to clean text.
        """

        if not text:

            return ""

        parser = HTMLTextExtractor()

        parser.feed(
            str(text)
        )

        cleaned = parser.get_text()

        cleaned = unescape(
            cleaned
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned
        )

        return cleaned.strip()

    # ==========================================================
    # TOPIC ID
    # ==========================================================

    def _generate_topic_id(
        self,
        url: str
    ) -> str:
        """
        Generate deterministic ID from URL.
        """

        digest = sha256(
            url.encode(
                "utf-8"
            )
        ).hexdigest()

        return (
            f"topic-{digest[:16]}"
        )

    # ==========================================================
    # PUBLISHED TIME
    # ==========================================================

    def _get_published_time(
        self,
        entry
    ) -> datetime:
        """
        Extract publication time.
        """

        parsed_time = None

        if hasattr(
            entry,
            "published_parsed"
        ):

            parsed_time = (
                entry.published_parsed
            )

        if not parsed_time and hasattr(
            entry,
            "updated_parsed"
        ):

            parsed_time = (
                entry.updated_parsed
            )

        if parsed_time:

            return datetime(
                parsed_time.tm_year,
                parsed_time.tm_mon,
                parsed_time.tm_mday,
                parsed_time.tm_hour,
                parsed_time.tm_min,
                parsed_time.tm_sec,
                tzinfo=timezone.utc
            )

        return datetime.now(
            timezone.utc
        )

    # ==========================================================
    # IMAGE EXTRACTION
    # ==========================================================

    def _get_image_url(
        self,
        entry
    ) -> str | None:
        """
        Try to extract an image URL from RSS metadata.
        """

        # media_content

        media_content = getattr(
            entry,
            "media_content",
            None
        )

        if media_content:

            for media in media_content:

                url = media.get(
                    "url"
                )

                if url:

                    return url

        # media_thumbnail

        media_thumbnail = getattr(
            entry,
            "media_thumbnail",
            None
        )

        if media_thumbnail:

            for media in media_thumbnail:

                url = media.get(
                    "url"
                )

                if url:

                    return url

        # enclosures

        enclosures = getattr(
            entry,
            "enclosures",
            None
        )

        if enclosures:

            for enclosure in enclosures:

                url = enclosure.get(
                    "href"
                ) or enclosure.get(
                    "url"
                )

                media_type = enclosure.get(
                    "type",
                    ""
                )

                if (
                    url
                    and media_type.startswith(
                        "image/"
                    )
                ):

                    return url

        return None

    # ==========================================================
    # CATEGORY DETECTION
    # ==========================================================

    def _detect_category(
        self,
        title: str,
        summary: str,
        source_name: str
    ) -> str:
        """
        Detect a more meaningful category.
        """

        text = (
            f"{title} {summary}"
        ).lower()

        categories = {

            "Cybersecurity": [
                "cybersecurity",
                "cyber security",
                "malware",
                "ransomware",
                "vulnerability",
                "exploit",
                "data breach",
                "security breach",
                "zero-day",
                "zero day",
            ],

            "Artificial Intelligence": [
                "artificial intelligence",
                "generative ai",
                "large language model",
                "language model",
                "machine learning",
                "deep learning",
                "ai model",
                "ai agent",
                "ai agents",
                "chatbot",
                "openai",
                "anthropic",
                "claude",
                "gpt",
                "gemini",
                "llm",
            ],

            "Robotics": [
                "robot",
                "robotics",
                "humanoid",
            ],

            "Cloud": [
                "cloud computing",
                "cloud infrastructure",
                "google cloud",
                "aws",
                "azure",
            ],

            "Hardware": [
                "gpu",
                "cpu",
                "chip",
                "processor",
                "semiconductor",
                "silicon",
                "hardware",
            ],

            "Open Source": [
                "open source",
                "open-source",
            ],

            "Developer": [
                "developer",
                "programming",
                "software development",
                "github",
                "api",
                "sdk",
            ],
        }

        # Give specific categories priority.

        for category, keywords in categories.items():

            for keyword in keywords:

                if keyword in text:

                    return category

        return "Technology"

    # ==========================================================
    # TAG GENERATION
    # ==========================================================

    def _generate_tags(
        self,
        title: str,
        summary: str
    ) -> list[str]:
        """
        Generate normalized tags.
        """

        text = (
            f"{title} {summary}"
        ).lower()

        keyword_map = {

            "AI": [
                "artificial intelligence",
                "generative ai",
                " ai ",
                "ai model",
                "ai agent",
            ],

            "LLM": [
                "llm",
                "language model",
                "large language model",
            ],

            "Cybersecurity": [
                "cybersecurity",
                "cyber security",
                "malware",
                "ransomware",
                "vulnerability",
                "zero-day",
            ],

            "Open Source": [
                "open source",
                "open-source",
            ],

            "Robotics": [
                "robot",
                "robotics",
                "humanoid",
            ],

            "Cloud": [
                "cloud computing",
                "cloud infrastructure",
                "google cloud",
                "aws",
                "azure",
            ],

            "GPU": [
                "gpu",
                "graphics processor",
            ],

            "Hardware": [
                "hardware",
                "chip",
                "processor",
                "semiconductor",
            ],

            "Machine Learning": [
                "machine learning",
            ],

            "Developer": [
                "developer",
                "github",
                "api",
                "sdk",
            ],
        }

        tags = []

        for tag, keywords in keyword_map.items():

            if any(
                keyword in text
                for keyword in keywords
            ):

                tags.append(
                    tag
                )

        return tags

    # ==========================================================
    # FILTER
    # ==========================================================

    def _filter_topics(
        self,
        topics: list[Topic]
    ) -> list[Topic]:
        """
        Remove obviously unsuitable RSS entries.
        """

        now = datetime.now(
            timezone.utc
        )

        filtered = []

        for topic in topics:

            # --------------------------------------------------
            # Empty title
            # --------------------------------------------------

            if not topic.title.strip():

                continue

            # --------------------------------------------------
            # Very old article
            # --------------------------------------------------

            age_seconds = (
                now - topic.published_at
            ).total_seconds()

            age_days = (
                age_seconds / 86400
            )

            if age_days > self.MAX_ARTICLE_AGE_DAYS:

                continue

            # --------------------------------------------------
            # Very short content
            # --------------------------------------------------

            if (
                len(topic.title) < 10
                and len(topic.summary) < 30
            ):

                continue

            filtered.append(
                topic
            )

        return filtered

    # ==========================================================
    # DEDUPLICATION
    # ==========================================================

    def _deduplicate(
        self,
        topics: list[Topic]
    ) -> list[Topic]:
        """
        Deduplicate by URL and normalized title.

        Important:
        We intentionally do NOT remove cross-source
        stories just because their titles are similar.

        Those will later be useful for verification.
        """

        seen_urls = set()

        seen_titles = set()

        unique_topics = []

        for topic in topics:

            normalized_url = (
                topic.url
                .strip()
                .rstrip("/")
                .lower()
            )

            normalized_title = re.sub(
                r"[^a-z0-9 ]",
                "",
                topic.title.lower()
            )

            normalized_title = re.sub(
                r"\s+",
                " ",
                normalized_title
            ).strip()

            # Exact URL duplicate.

            if normalized_url in seen_urls:

                continue

            # Exact title duplicate from the same
            # collection.

            if normalized_title in seen_titles:

                continue

            seen_urls.add(
                normalized_url
            )

            seen_titles.add(
                normalized_title
            )

            unique_topics.append(
                topic
            )

        return unique_topics

    # ==========================================================
    # STATUS
    # ==========================================================

    def get_status(self) -> dict:
        """
        Return collector statistics.
        """

        return {

            "last_collection_time":
                self.last_collection_time,

            "total_before_deduplication":
                self.total_before_deduplication,

            "total_collected":
                self.total_collected,

            "feeds":
                self.feed_statistics,

            "errors":
                self.last_errors,
        }

    # ==========================================================
    # CLEANUP
    # ==========================================================

    def close(self):
        """
        Close the HTTP session.
        """

        self.session.close()