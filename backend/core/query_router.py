import os
import requests


class QueryRouter:
    """
    Fast query classifier that decides whether a query should go to:
    - SQL: For exact user data (marks, profile, availability)
    - RAG: For general campus knowledge (rules, history, departments)
    - HYBRID: When both are needed
    """

    SQL_KEYWORDS = [
        "my marks", "my data", "my profile", "my cgpa", "my usn",
        "my semester", "my subjects", "my attendance",
        "is available", "available now", "available right now",
        "staff schedule", "faculty schedule",
        "when can i meet", "can i meet", "meet professor",
        "meet mam", "meet sir", "meet ma'am", "meet madam",
        "is she available", "is he available",
        "who is available", "which faculty", "which professor",
    ]

    RAG_KEYWORDS = [
        "about dsce", "about college", "history", "placement",
        "department", "admission", "hostel", "library",
        "campus", "facilities", "research", "exam",
        "syllabus", "fee", "scholarship", "club",
        "event", "fest", "catalysis", "hackathon", "workshop",
        "rule", "regulation", "accreditation",
        "principal", "chairman", "naac", "nba", "vtu",
        "address", "contact", "phone", "email",
        "courses", "programs", "phd", "mtech", "mba", "mca",
        "newsletter", "sports", "canteen",
        "how to", "what is", "tell me about", "explain",
        "who is", "when was", "where is",
        "notice", "letter", "application", "bonafide", "certificate",
    ]

    # Keywords that suggest the user wants BOTH faculty data AND knowledge
    HYBRID_TRIGGERS = [
        "available", "schedule", "faculty", "teacher", "professor",
        "staff", "meet", "mam", "sir", "ma'am", "madam",
    ]

    def __init__(self, groq_api_key):
        self.api_key = groq_api_key

    def classify(self, query: str) -> str:
        q = query.lower().strip()

        has_sql = any(kw in q for kw in self.SQL_KEYWORDS)
        has_rag = any(kw in q for kw in self.RAG_KEYWORDS)
        has_hybrid = any(kw in q for kw in self.HYBRID_TRIGGERS)

        # If SQL keywords match
        if has_sql:
            return "HYBRID" if has_rag else "SQL"

        # If hybrid triggers found (faculty/meet/available)
        if has_hybrid:
            return "HYBRID"

        # If RAG keywords match
        if has_rag:
            return "RAG"

        # Default to RAG for general knowledge questions
        return "RAG"


if __name__ == "__main__":
    router = QueryRouter("test")
    tests = [
        ("Tell me about college placements", "RAG"),
        ("What are my marks?", "SQL"),
        ("When can I meet Shreya mam", "HYBRID"),
        ("Is Shreya available right now?", "HYBRID"),
        ("What is the admission process?", "RAG"),
        ("Who is the principal?", "RAG"),
        ("Is there any events going on", "RAG"),
        ("What is catalysis v4", "RAG"),
        ("staff faculty availability", "HYBRID"),
        ("Which faculty is available?", "HYBRID"),
    ]
    for q, expected in tests:
        result = router.classify(q)
        status = "✅" if result == expected else "❌"
        print(f"{status} Q: '{q}' -> {result} (expected: {expected})")
