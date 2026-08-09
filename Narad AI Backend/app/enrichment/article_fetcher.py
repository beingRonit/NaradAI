"""
Article Enrichment Engine.

Fetches richer article content from Topic URLs.

The engine is designed for repeated editorial cycles.

Example:

    Cycle 1
        Attempt enrichment
        ↓
        Failed
        ↓
        Preserve RSS content

    Cycle 2
        Retry
        ↓
        Failed

    Cycle 3
        Retry
        ↓
        Success
        ↓
        Cache article

    Cycle 4
        Use cached article
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import requests
try:
    import trafilatura
except ImportError:
    trafilatura = None

from bs4 import BeautifulSoup

from app.agent.models import (
    Topic,
    EnrichmentStatus,
)


# ==========================================================
# ENRICHMENT RESULT
# ==========================================================

@dataclass
class EnrichmentResult:

    topic_id: str

    success: bool

    content: str

    original_content_length: int

    enriched_content_length: int

    status_code: Optional[int]

    final_url: Optional[str]

    extractor: Optional[str]

    error: Optional[str]

    attempt_number: int

    fetched_at: datetime


# ==========================================================
# ARTICLE FETCHER
# ==========================================================

class ArticleFetcher:

    DEFAULT_TIMEOUT = 20

    MAX_CONTENT_LENGTH = 100_000

    MIN_ARTICLE_LENGTH = 300

    # Retry delays in minutes. Attempt 1 is immediate; subsequent
    # failures wait progressively longer before another HTTP request.
    RETRY_DELAYS_MINUTES = (30, 60, 120, 360)
    MAX_RETRY_ATTEMPTS = 5

    USER_AGENT = (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0.0.0 "
        "Safari/537.36"
    )

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT
    ):

        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": self.USER_AGENT,

                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "*/*;q=0.8"
                ),

                "Accept-Language":
                    "en-US,en;q=0.9",

                "Accept-Encoding":
                    "gzip, deflate",

                "Connection":
                    "keep-alive",
            }
        )

        self.processed_count = 0

        self.success_count = 0

        self.failure_count = 0

        self.skipped_count = 0

    # ======================================================
    # CYCLE STATISTICS
    # ======================================================

    def reset_cycle_stats(self) -> None:
        """Reset counters so get_status() reports this cycle only."""
        self.processed_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.skipped_count = 0

    # ======================================================
    # ENRICH
    # ======================================================

    def enrich(
        self,
        topic: Topic,
        force: bool = False
    ) -> EnrichmentResult:

        now = datetime.utcnow()

        # --------------------------------------------------
        # USE CACHED ARTICLE
        # --------------------------------------------------

        if (
            topic.enrichment_status
            == EnrichmentStatus.SUCCESS
            and not force
        ):

            self.skipped_count += 1

            return EnrichmentResult(

                topic_id=topic.id,

                success=True,

                content=topic.content or "",

                original_content_length=len(
                    topic.content or ""
                ),

                enriched_content_length=(
                    topic.enriched_content_length
                ),

                status_code=200,

                final_url=topic.url,

                extractor="cached",

                error=None,

                attempt_number=(
                    topic.enrichment_attempts
                ),

                fetched_at=now
            )

        # --------------------------------------------------
        # RETRY BACKOFF
        # --------------------------------------------------
        # Failed enrichment is retryable, but never on every cycle.
        # `force=True` is reserved for explicit/manual retries.
        retry_at = getattr(topic, "next_enrichment_retry", None)
        if (
            topic.enrichment_status == EnrichmentStatus.FAILED
            and retry_at is not None
            and now < retry_at
            and not force
        ):
            self.skipped_count += 1
            return EnrichmentResult(
                topic_id=topic.id,
                success=False,
                content=topic.content or "",
                original_content_length=len(topic.content or ""),
                enriched_content_length=topic.enriched_content_length,
                status_code=None,
                final_url=topic.url,
                extractor="backoff",
                error=(
                    f"Retry deferred until {retry_at.isoformat()}."
                ),
                attempt_number=topic.enrichment_attempts,
                fetched_at=now,
            )

        if (
            topic.enrichment_status == EnrichmentStatus.FAILED
            and topic.enrichment_attempts >= self.MAX_RETRY_ATTEMPTS
            and not force
        ):
            self.skipped_count += 1
            return EnrichmentResult(
                topic_id=topic.id,
                success=False,
                content=topic.content or "",
                original_content_length=len(topic.content or ""),
                enriched_content_length=topic.enriched_content_length,
                status_code=None,
                final_url=topic.url,
                extractor="cooldown",
                error="Maximum automatic enrichment retries reached; cooldown active.",
                attempt_number=topic.enrichment_attempts,
                fetched_at=now,
            )

        self.processed_count += 1

        # --------------------------------------------------
        # REGISTER ATTEMPT
        # --------------------------------------------------

        topic.enrichment_attempts += 1

        topic.last_enrichment_attempt = now

        topic.enrichment_status = (
            EnrichmentStatus.PENDING
        )

        topic.enrichment_error = None

        attempt_number = (
            topic.enrichment_attempts
        )

        # --------------------------------------------------
        # PRESERVE ORIGINAL RSS CONTENT
        # --------------------------------------------------

        original_content = (
            topic.content or ""
        )

        original_length = len(
            original_content
        )

        # --------------------------------------------------
        # URL VALIDATION
        # --------------------------------------------------

        if not topic.url:

            return self._failure(
                topic=topic,
                original_content=original_content,
                attempt_number=attempt_number,
                status_code=None,
                final_url=None,
                error="Topic has no URL."
            )

        # --------------------------------------------------
        # HTTP REQUEST
        # --------------------------------------------------

        try:

            response = self.session.get(
                topic.url,
                timeout=self.timeout,
                allow_redirects=True
            )

        except requests.exceptions.Timeout:

            return self._failure(
                topic=topic,
                original_content=original_content,
                attempt_number=attempt_number,
                status_code=None,
                final_url=None,
                error="Request timed out."
            )

        except requests.exceptions.RequestException as exc:

            return self._failure(
                topic=topic,
                original_content=original_content,
                attempt_number=attempt_number,
                status_code=None,
                final_url=None,
                error=str(exc)
            )

        # --------------------------------------------------
        # RESPONSE DATA
        # --------------------------------------------------

        status_code = response.status_code

        final_url = str(
            response.url
        )

        content_type = (
            response.headers
            .get(
                "Content-Type",
                ""
            )
            .lower()
        )

        # --------------------------------------------------
        # HTTP STATUS
        # --------------------------------------------------

        if status_code != 200:

            return self._failure(
                topic=topic,
                original_content=original_content,
                attempt_number=attempt_number,
                status_code=status_code,
                final_url=final_url,
                error=(
                    f"Server returned HTTP "
                    f"{status_code}."
                )
            )

        # --------------------------------------------------
        # CONTENT TYPE
        # --------------------------------------------------

        if "html" not in content_type:

            return self._failure(
                topic=topic,
                original_content=original_content,
                attempt_number=attempt_number,
                status_code=status_code,
                final_url=final_url,
                error=(
                    "Response is not HTML. "
                    f"Content-Type: {content_type}"
                )
            )

        html = response.text

        if not html.strip():

            return self._failure(
                topic=topic,
                original_content=original_content,
                attempt_number=attempt_number,
                status_code=status_code,
                final_url=final_url,
                error="Server returned empty HTML."
            )

        # --------------------------------------------------
        # EXTRACTION 1
        # --------------------------------------------------

        extracted = (
            self._extract_with_trafilatura(
                html
            )
        )

        if extracted:

            return self._success(
                topic=topic,
                original_content=original_content,
                content=extracted,
                attempt_number=attempt_number,
                status_code=status_code,
                final_url=final_url,
                extractor="trafilatura"
            )

        # --------------------------------------------------
        # EXTRACTION 2
        # --------------------------------------------------

        extracted = (
            self._extract_with_beautifulsoup(
                html
            )
        )

        if extracted:

            return self._success(
                topic=topic,
                original_content=original_content,
                content=extracted,
                attempt_number=attempt_number,
                status_code=status_code,
                final_url=final_url,
                extractor="beautifulsoup"
            )

        # --------------------------------------------------
        # FAILED EXTRACTION
        # --------------------------------------------------

        return self._failure(
            topic=topic,
            original_content=original_content,
            attempt_number=attempt_number,
            status_code=status_code,
            final_url=final_url,
            error=(
                "HTML was received but no readable "
                "article content could be extracted."
            )
        )

    # ======================================================
    # TRAFILATURA
    # ======================================================

    def _extract_with_trafilatura(
        self,
        html: str
    ) -> Optional[str]:

        try:

            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                include_links=False,
                include_images=False,
                favor_precision=True,
                deduplicate=True,
            )

        except Exception:

            return None

        if not text:

            return None

        text = self._clean_text(
            text
        )

        if len(text) < self.MIN_ARTICLE_LENGTH:

            return None

        return self._limit_content(
            text
        )

    # ======================================================
    # BEAUTIFULSOUP
    # ======================================================

    def _extract_with_beautifulsoup(
        self,
        html: str
    ) -> Optional[str]:

        try:

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

        except Exception:

            return None

        # --------------------------------------------------
        # REMOVE NON-ARTICLE ELEMENTS
        # --------------------------------------------------

        for element in soup(
            [
                "script",
                "style",
                "noscript",
                "svg",
                "nav",
                "footer",
                "header",
                "form",
                "aside",
                "iframe",
            ]
        ):

            element.decompose()

        # --------------------------------------------------
        # ARTICLE ELEMENT
        # --------------------------------------------------

        article = soup.find(
            "article"
        )

        if article:

            text = article.get_text(
                separator=" ",
                strip=True
            )

            text = self._clean_text(
                text
            )

            if len(text) >= self.MIN_ARTICLE_LENGTH:

                return self._limit_content(
                    text
                )

        # --------------------------------------------------
        # PARAGRAPH FALLBACK
        # --------------------------------------------------

        paragraphs = soup.find_all(
            "p"
        )

        paragraph_text = []

        for paragraph in paragraphs:

            text = paragraph.get_text(
                separator=" ",
                strip=True
            )

            text = self._clean_text(
                text
            )

            if len(text) >= 40:

                paragraph_text.append(
                    text
                )

        combined = " ".join(
            paragraph_text
        )

        combined = self._clean_text(
            combined
        )

        if len(combined) >= self.MIN_ARTICLE_LENGTH:

            return self._limit_content(
                combined
            )

        return None

    # ======================================================
    # SUCCESS
    # ======================================================

    def _success(
        self,
        topic: Topic,
        original_content: str,
        content: str,
        attempt_number: int,
        status_code: int,
        final_url: str,
        extractor: str
    ) -> EnrichmentResult:

        now = datetime.utcnow()

        topic.content = content

        topic.enrichment_status = (
            EnrichmentStatus.SUCCESS
        )

        topic.last_enrichment_success = now

        topic.enrichment_error = None
        topic.next_enrichment_retry = None

        topic.enriched_content_length = len(
            content
        )

        self.success_count += 1

        return EnrichmentResult(

            topic_id=topic.id,

            success=True,

            content=content,

            original_content_length=len(
                original_content
            ),

            enriched_content_length=len(
                content
            ),

            status_code=status_code,

            final_url=final_url,

            extractor=extractor,

            error=None,

            attempt_number=attempt_number,

            fetched_at=now
        )

    # ======================================================
    # FAILURE
    # ======================================================

    def _failure(
        self,
        topic: Topic,
        original_content: str,
        attempt_number: int,
        status_code: Optional[int],
        final_url: Optional[str],
        error: str
    ) -> EnrichmentResult:

        now = datetime.utcnow()

        topic.enrichment_status = (
            EnrichmentStatus.FAILED
        )

        topic.enrichment_error = error

        # Schedule the next automatic attempt. Repeated failures use
        # progressively longer delays; the final automatic attempt
        # enters cooldown until explicitly forced.
        if attempt_number < self.MAX_RETRY_ATTEMPTS:
            delay_index = min(
                attempt_number - 1,
                len(self.RETRY_DELAYS_MINUTES) - 1,
            )
            topic.next_enrichment_retry = (
                datetime.utcnow()
                + timedelta(
                    minutes=self.RETRY_DELAYS_MINUTES[delay_index]
                )
            )
        else:
            topic.next_enrichment_retry = None

        # --------------------------------------------------
        # CRITICAL:
        #
        # Never delete RSS content because enrichment failed.
        # --------------------------------------------------

        topic.content = original_content

        topic.enriched_content_length = 0

        self.failure_count += 1

        return EnrichmentResult(

            topic_id=topic.id,

            success=False,

            content=original_content,

            original_content_length=len(
                original_content
            ),

            enriched_content_length=len(
                original_content
            ),

            status_code=status_code,

            final_url=final_url,

            extractor=None,

            error=error,

            attempt_number=attempt_number,

            fetched_at=now
        )

    # ======================================================
    # TEXT CLEANING
    # ======================================================

    def _clean_text(
        self,
        text: str
    ) -> str:

        if not text:

            return ""

        text = " ".join(
            text.split()
        )

        return text.strip()

    # ======================================================
    # CONTENT LIMIT
    # ======================================================

    def _limit_content(
        self,
        content: str
    ) -> str:

        if len(content) <= self.MAX_CONTENT_LENGTH:

            return content

        return content[
            :self.MAX_CONTENT_LENGTH
        ]

    # ======================================================
    # BATCH
    # ======================================================

    def enrich_many(
        self,
        topics: list[Topic],
        force: bool = False
    ) -> list[EnrichmentResult]:

        results = []

        for topic in topics:

            results.append(
                self.enrich(
                    topic,
                    force=force
                )
            )

        return results

    # ======================================================
    # STATUS
    # ======================================================

    def get_status(self) -> dict:

        return {
            "processed":
                self.processed_count,

            "successful":
                self.success_count,

            "failed":
                self.failure_count,

            "skipped":
                self.skipped_count,
        }

    # ======================================================
    # CLOSE
    # ======================================================

    def close(self):

        self.session.close()