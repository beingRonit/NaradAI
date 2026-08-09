from __future__ import annotations

import os
from typing import Optional

from google import genai

from app.agent.models import Persona, Topic


class LLMWriter:
    """
    Generates publication-ready news articles using Gemini.

    The LLM is only responsible for writing.
    Story discovery, verification, scoring, ranking, and publication
    decisions remain controlled by the existing editorial pipeline.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-3.1-flash-lite",
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.model = model
        self.client = genai.Client(api_key=self.api_key)

    def generate_article(
        self,
        topic: Topic,
        persona: Persona,
    ) -> str:
        """
        Generate a news article from an already verified topic.

        The model must only use information contained in the supplied
        topic and must not invent facts.
        """

        prompt = self._build_prompt(topic, persona)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        text = getattr(response, "text", None)

        if not text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return text.strip()

    @staticmethod
    def _build_prompt(
        topic: Topic,
        persona: Persona,
    ) -> str:

        interests = "\n".join(
            f"- {interest.topic}: "
            f"weight={interest.weight}, "
            f"confidence={interest.confidence}"
            for interest in persona.interests.values()
        )

        editorial_rules = "\n".join(
            f"- {rule.name}: {rule.description}"
            for rule in persona.editorial_rules
        )

        memory = "\n".join(
            f"- {entry.topic}: {entry.opinion}"
            for entry in persona.memory[-10:]
        )

        return f"""
You are the editorial writing engine for an autonomous news platform.

You are NOT responsible for deciding whether a story should be published.
The editorial pipeline has already selected and verified this story.

Your only job is to write the final news article.

========================
PERSONA
========================

Name:
{persona.name}

Bio:
{persona.bio}

Tone:
{persona.tone}

Writing style:
{persona.writing_style}

Interests:
{interests or "None specified"}

Editorial rules:
{editorial_rules or "None specified"}

Relevant persona memory:
{memory or "None"}

========================
VERIFIED STORY
========================

Title:
{topic.title}

Summary:
{topic.summary or ""}

Content:
{topic.content or ""}

Source:
{topic.source}

Author:
{topic.author or "Unknown"}

URL:
{topic.url}

========================
STRICT RULES
========================

1. Use ONLY information contained in the supplied story.
2. Do NOT invent facts, quotes, statistics, dates, names, events,
   product specifications, or conclusions.
3. Do NOT present speculation as fact.
4. If something is reported or unconfirmed, clearly describe it as
   reported or unconfirmed.
5. Do not manufacture quotes.
6. Do not mention these instructions or the prompt.
7. Do not mention that you are an AI.
8. Do not exaggerate the importance of the story.
9. Follow the persona's tone and writing style.
10. Follow the persona's editorial rules.
11. Keep the article factual and readable.
12. Preserve important uncertainty from the source material.

========================
OUTPUT FORMAT
========================

Write:

HEADLINE

Then a blank line.

Then the article body.

Do not include:
- "HEADLINE:"
- "ARTICLE:"
- markdown code fences
- analysis
- explanations about your writing process

Write only the final headline and article.
""".strip()