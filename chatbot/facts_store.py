from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class FactEntry:
    """Structured fact answer for very common intents.

    These are short, precise, manually curated snippets so that
    we avoid hallucination for critical queries like location,
    fees, facilities, and examinations.
    """

    key: str
    answer: str


# NOTE: These values are intentionally short and factual.
# You can update / extend them later directly in this file
# if any detail changes on the official website.
FACTS: Dict[str, FactEntry] = {
    "location": FactEntry(
        key="location",
        answer=(
            "Dayananda Sagar College of Engineering (DSCE) is located at "
            "Kumaraswamy Layout, Bangalore – 560 111, Karnataka, India."
        ),
    ),
    "facilities": FactEntry(
        key="facilities",
        answer=(
            "The college provides major on-campus facilities including a hospital, "
            "library, hostels, data center, sports and fitness infrastructure, "
            "counselling center, yoga and meditation center, and a centre for "
            "performing arts. For full details, refer to the Facilities section on "
            "the official DSCE website."
        ),
    ),
    "fees": FactEntry(
        key="fees",
        answer=(
            "Fee details for various programs are published in the 'Fee Structure' "
            "section under Admissions on the official DSCE website. Please refer to "
            "that page for the latest and most accurate fee information."
        ),
    ),
    "examinations": FactEntry(
        key="examinations",
        answer=(
            "Examination-related notifications, timetables, and circulars are "
            "published in the Examination section of the official DSCE website. "
            "Students should regularly check that section for the latest updates."
        ),
    ),
}


INTENT_KEYWORDS = {
    "location": [
        "where is the college",
        "college location",
        "where is dsce",
        "address",
        "kumaraswamy",
        "bangalore location",
    ],
    "facilities": [
        "facilities",
        "facility",
        "campus facilities",
        "infrastructure",
        "hostel facilities",
        "library facilities",
    ],
    "fees": [
        "fees",
        "fee structure",
        "academic fees",
        "course fee",
        "tuition fee",
    ],
    "examinations": [
        "exam",
        "examination",
        "exam notification",
        "exam notifications",
        "examination notifications",
        "exam timetable",
        "examination timetable",
    ],
}


def detect_fact_key(question: str) -> Optional[str]:
    """Return a fact key if the user question clearly matches one of our intents."""
    q = question.lower()

    for key, phrases in INTENT_KEYWORDS.items():
        for phrase in phrases:
            if phrase in q:
                return key

    # Also support simple keyword-based mapping for short queries
    if "fees" in q or "fee" in q:
        return "fees"
    if "facility" in q or "facilities" in q or "infrastructure" in q:
        return "facilities"
    if "exam" in q or "examination" in q:
        return "examinations"
    if "location" in q or "address" in q:
        return "location"

    return None


def get_fact_answer(question: str) -> Optional[str]:
    """Return a structured fact answer if this question matches a known intent."""
    key = detect_fact_key(question)
    if key is None:
        return None
    entry = FACTS.get(key)
    return entry.answer if entry is not None else None

