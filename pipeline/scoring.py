"""This module handles the scoring step of the pipeline, evaluating each lead based on deterministic rules to assign a score that reflects their potential fit and engagement level.
Leads that fail basic qualification checks are filtered out at this stage."""

import json
from pathlib import Path
from pipeline.sources.base import RawLead

# Load scoring weights from JSON file
_weights_path = Path(__file__).parent.parent / "scoring_weights.json"
_Weights = json.loads(_weights_path.read_text())


# ── Scored lead model ─────────────────────────────────────────────────────────


class ScoredLead(RawLead):
    score: int = 0
    selected: bool = False


# ── Disqualification rules ────────────────────────────────────────────────────

DISQUALIFIED_TITLES = {
    "sales",
    "account executive",
    "account manager",
    "business development",
    "marketing",
    "recruiter",
    "recruiting",
    "talent",
    "human resources",
    "hr",
    "legal",
    "finance",
    "accountant",
    "operations manager",
    "office manager",
}


def is_disqualified(lead: RawLead) -> tuple[bool, str]:
    if not lead.name or not lead.company:
        return True, "missing name or company"

    if any(t in lead.title.lower() for t in DISQUALIFIED_TITLES):
        return True, f"non-technical role: {lead.title}"

    return False, ""


# ── Deterministic scoring ─────────────────────────────────────────────────────

SENIORITY_SCORES = {
    "high": (
        ["vp", "vice president", "director", "head of", "cto", "cio"],
        _Weights["seniority"]["high"],
    ),
    "mid_high": (
        ["staff", "principal", "lead", "architect"],
        _Weights["seniority"]["mid_high"],
    ),
    "mid": (["senior", "manager"], _Weights["seniority"]["mid"]),
    "entry": (
        ["engineer", "developer", "analyst", "scientist"],
        _Weights["seniority"]["entry"],
    ),
}

TECHNICAL_DOMAIN_TERMS = [
    "data",
    "platform",
    "infrastructure",
    "backend",
    "database",
    "distributed",
    "systems",
    "reliability",
    "sre",
    "devops",
]

CASSANDRA_SIGNAL_TERMS = [
    "cassandra",
    "datastax",
    "astra",
    "cql",
    "cqlsh",
    "nosql",
    "wide column",
    "time series",
]

ENGAGEMENT_SIGNAL_TERMS = [
    "speaker",
    "contributor",
    "open source",
    "author",
    "maintainer",
    "conference",
    "summit",
    "blog",
]


def score_lead(lead: RawLead) -> int:
    score = 0
    combined = f"{lead.title.lower()} {lead.notes.lower()}"

    # Seniority — max 40 pts
    for _, (keywords, pts) in SENIORITY_SCORES.items():
        if any(k in lead.title.lower() for k in keywords):
            score += pts
            break

    # Technical domain relevance
    score += min(
        sum(1 for t in TECHNICAL_DOMAIN_TERMS if t in combined)
        * _Weights["domain"]["per_term"],
        _Weights["domain"]["max"],
    )

    # Cassandra/DataStax signal
    score += min(
        sum(1 for t in CASSANDRA_SIGNAL_TERMS if t in combined)
        * _Weights["cassandra"]["per_term"],
        _Weights["cassandra"]["max"],
    )

    # Engagement signal
    if any(t in combined for t in ENGAGEMENT_SIGNAL_TERMS):
        score += _Weights["engagement"]

    return min(score, 100)


# ── Entry point ───────────────────────────────────────────────────────────────


def process(lead: RawLead) -> tuple[ScoredLead | None, str]:
    disqualified, reason = is_disqualified(lead)
    if disqualified:
        return None, reason

    scored = ScoredLead(**lead.model_dump(), score=score_lead(lead))

    # TODO: after deterministic scoring, add an LLM-based rating step.
    # For leads that pass the threshold, call the LLM with the full lead profile and ask it
    # to rate the lead 1-10 based on likelihood of operational pain and openness
    # to evaluating an alternative. This catches nuanced cases the rule-based scorer misses.
    # Only run this in live mode to avoid token cost during mock/dev runs.
    # Example: scored = await llm_rate_lead(scored) if not mock else scored.

    return scored, ""
