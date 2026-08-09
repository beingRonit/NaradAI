"""Persona lifecycle, defaults, and durable persona memory."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from app.agent.models import Persona, Interest, EditorialRule, MemoryEntry


class PersonaEngine:
    def __init__(self, persistence_path: str | None = None):
        self.persistence_path = Path(persistence_path) if persistence_path else None
        self.persona = None
        if self.persistence_path:
            self._load()

    def create_default_persona(self):
        self.persona = Persona(
            name="Narad",
            bio="Senior AI Research Engineer specializing in Artificial Intelligence and Cybersecurity.",
            tone="Analytical",
            writing_style="Evidence Driven",
            posting_time="09:00",
            timezone="Asia/Kolkata",
        )
        self._install_defaults()
        self._save()
        return self.persona

    def ensure_default_persona(self):
        if self.persona is None:
            return self.create_default_persona()
        self._install_defaults()
        self._save()
        return self.persona

    def _install_defaults(self):
        defaults = [
            ("LLMs", 95.0, 0.95),
            ("Artificial Intelligence", 95.0, 0.95),
            ("Machine Learning", 90.0, 0.9),
            ("Cybersecurity", 90.0, 0.9),
            ("Software Engineering", 80.0, 0.85),
            ("Cloud", 75.0, 0.8),
            ("Robotics", 65.0, 0.75),
        ]
        existing_interest_keys = {
            str(key).strip().lower()
            for key in self.persona.interests.keys()
        }
        for topic, weight, confidence in defaults:
            if topic.strip().lower() not in existing_interest_keys:
                self.persona.interests[topic] = Interest(topic=topic, weight=weight, confidence=confidence)
                existing_interest_keys.add(topic.strip().lower())

        rule_names = {r.name.strip().lower() for r in self.persona.editorial_rules}
        rules = [
            ("Avoid Hype", "Never exaggerate AI news.", 10),
            ("Prefer Evidence", "Prefer specific claims with identifiable evidence.", 9),
            ("Prefer Technical Substance", "Prefer meaningful technical developments over generic announcements.", 8),
        ]
        for name, description, priority in rules:
            if name.lower() not in rule_names:
                self.persona.editorial_rules.append(EditorialRule(name=name, description=description, priority=priority))

    def get_persona(self):
        return self.persona

    def add_interest(self, topic: str, weight: float = 50.0, confidence: float = 0.5):
        if self.persona is None:
            raise RuntimeError("No Persona loaded.")
        interest = Interest(topic=topic, weight=weight, confidence=confidence)
        self.persona.interests[topic] = interest
        self._save()
        return interest

    def get_interest(self, topic: str):
        if self.persona is None:
            raise RuntimeError("No Persona loaded.")
        return self.persona.interests.get(topic)

    def update_interest(self, topic: str, weight_delta: float):
        if self.persona is None:
            raise RuntimeError("No Persona loaded.")
        interest = self.persona.interests.get(topic)
        if interest is None:
            return None
        interest.weight = max(0.0, min(100.0, interest.weight + weight_delta))
        interest.interactions += 1
        interest.last_updated = datetime.utcnow()
        self._save()
        return interest

    def remove_interest(self, topic: str):
        if self.persona is None:
            raise RuntimeError("No Persona loaded.")
        self.persona.interests.pop(topic, None)
        self._save()

    def add_editorial_rule(self, name: str, description: str, priority: int):
        if self.persona is None:
            raise RuntimeError("No Persona loaded.")
        rule = EditorialRule(name=name, description=description, priority=priority)
        self.persona.editorial_rules.append(rule)
        self._save()
        return rule

    def add_memory(self, topic: str, opinion: str, keywords=None, companies=None, technologies=None):
        if self.persona is None:
            raise RuntimeError("No Persona loaded.")
        key = " ".join(topic.lower().split())
        for item in self.persona.memory:
            if " ".join(item.topic.lower().split()) == key:
                return item
        memory = MemoryEntry(topic=topic, opinion=opinion, keywords=keywords or [], companies=companies or [], technologies=technologies or [])
        self.persona.memory.append(memory)
        self._save()
        return memory

    def summary(self):
        if self.persona is None:
            raise RuntimeError("No Persona loaded.")
        return {
            "Name": self.persona.name,
            "Status": self.persona.state.status.value,
            "Interests": len(self.persona.interests),
            "Rules": len(self.persona.editorial_rules),
            "Memory": len(self.persona.memory),
        }

    def _save(self):
        if not self.persistence_path or self.persona is None:
            return
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self.persona)
        with self.persistence_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False, default=str)

    def _load(self):
        try:
            data = json.loads(self.persistence_path.read_text(encoding="utf-8"))
            self.persona = Persona(
                name=data["name"], bio=data["bio"], tone=data["tone"],
                writing_style=data["writing_style"], posting_time=data["posting_time"], timezone=data["timezone"],
            )
            for key, row in data.get("interests", {}).items():
                self.persona.interests[key] = Interest(**{k: v for k, v in row.items() if k in {"topic", "weight", "confidence", "interactions"}})
            self.persona.editorial_rules = [EditorialRule(**{k: row[k] for k in ("name", "description", "priority", "enabled") if k in row}) for row in data.get("editorial_rules", [])]
            self.persona.memory = [MemoryEntry(**{k: row[k] for k in ("topic", "opinion", "keywords", "companies", "technologies") if k in row}) for row in data.get("memory", [])]
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.persona = None
