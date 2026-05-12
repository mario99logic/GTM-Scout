"""Handles all persistence — saving leads, messages, and reports to the database, and exporting results to CSV and JSON."""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from db.session import SessionLocal
from db.models import Lead, Message, Report
from pipeline.scoring import ScoredLead
from pipeline.personalization import PersonalisedMessages
from config import settings


# ── Called once per pipeline run ──────────────────────────────────────────────


def create_report(lead_source: str) -> str:
    """Create a report row at the start of a run. Returns the report ID."""
    with SessionLocal() as db:
        report = Report(
            started_at=datetime.now(timezone.utc),
            dry_run=settings.dry_run,
            lead_source=lead_source,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report.id


# ── Called after a lead passes the filter ─────────────────────────────────────


def save_lead(report_id: str, lead: ScoredLead) -> str:
    """Persist a qualified lead. Returns the lead ID."""
    with SessionLocal() as db:
        row = Lead(
            report_id=report_id,
            name=lead.name,
            title=lead.title,
            company=lead.company,
            linkedin_url=lead.linkedin_url,
            score=lead.score,
            source=lead.source,
            status="qualified",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id


# ── Called after trigger fires (messages sent or dry-run logged) ──────────────


def save_messages(lead_id: str, messages: PersonalisedMessages) -> None:
    """Persist the generated LinkedIn invite and follow-up email."""
    with SessionLocal() as db:
        db.add_all(
            [
                Message(
                    lead_id=lead_id,
                    type="linkedin_invite",
                    body=messages.invite.body,
                    dry_run=settings.dry_run,
                    llm_model=settings.anthropic_model,
                ),
                Message(
                    lead_id=lead_id,
                    type="follow_up_email",
                    subject=messages.email.subject,
                    body=messages.email.body,
                    dry_run=settings.dry_run,
                    llm_model=settings.anthropic_model,
                ),
            ]
        )
        db.commit()


def update_lead_status(lead_id: str, status: str) -> None:
    with SessionLocal() as db:
        lead = db.get(Lead, lead_id)
        lead.status = status
        db.commit()


# ── Called once at the end of the run ────────────────────────────────────────


def finish_report(report_id: str, stats: dict) -> None:
    """Update the report with final counts and export CSV + JSON."""
    with SessionLocal() as db:
        report = db.get(Report, report_id)
        report.finished_at = datetime.now(timezone.utc)
        report.total_found = stats["total_found"]
        report.total_qualified = stats["total_qualified"]
        report.total_selected = stats["total_selected"]
        report.total_messaged = stats["total_messaged"]
        db.commit()

    _export(report_id)


def _export(report_id: str) -> None:
    with SessionLocal() as db:
        leads = db.query(Lead).filter_by(report_id=report_id).all()

        rows = []
        for lead in leads:
            msgs = db.query(Message).filter_by(lead_id=lead.id).all()
            invite = next((m.body for m in msgs if m.type == "linkedin_invite"), "")
            email_subject = next(
                (m.subject for m in msgs if m.type == "follow_up_email"), ""
            )
            email_body = next((m.body for m in msgs if m.type == "follow_up_email"), "")
            rows.append(
                {
                    "name": lead.name,
                    "title": lead.title,
                    "company": lead.company,
                    "linkedin_url": lead.linkedin_url,
                    "score": lead.score,
                    "status": lead.status,
                    "linkedin_invite": invite,
                    "email_subject": email_subject,
                    "email_body": email_body,
                }
            )

    if not rows:
        print("[WARNING] No leads found for this report.")
        return

    out = Path(settings.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    csv_path = out / f"report_{report_id[:8]}.csv"
    json_path = out / f"report_{report_id[:8]}.json"

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    with open(json_path, "w") as f:
        json.dump(rows, f, indent=2)

    print(f"\nReport exported to {csv_path} and {json_path}")
