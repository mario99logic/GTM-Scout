"""Handles the trigger step — in dry-run mode it logs what would have been sent, in live mode it calls the real LinkedIn and email APIs."""

import json
from datetime import datetime, timezone
from pathlib import Path

from config import settings
from pipeline.scoring import ScoredLead
from pipeline.personalization import PersonalisedMessages


def trigger(lead: ScoredLead, messages: PersonalisedMessages, dry_run: bool) -> dict:
    """Trigger the outreach actions for a qualified lead.
    In dry-run mode, it logs the messages that would have been sent.
    In live mode, it sends the LinkedIn invite and follow-up email."""
    timestamp = datetime.now(timezone.utc).isoformat()

    result = {
        "lead_name": lead.name,
        "lead_title": lead.title,
        "lead_company": lead.company,
        "linkedin_url": lead.linkedin_url,
        "score": lead.score,
        "dry_run": dry_run,
        "timestamp": timestamp,
        "linkedin_invite": messages.invite.body,
        "email_subject": messages.email.subject,
        "email_body": messages.email.body,
        "status": "dry_run" if dry_run else "sent",
    }

    if dry_run:
        _log(result)
    else:
        _send_linkedin(lead, messages.invite.body)
        _send_email(lead, messages.email)

    return result


def _log(result: dict):
    print(f"\n{'─' * 60}")
    print(
        f"DRY RUN — {result['lead_name']} | {result['lead_title']} @ {result['lead_company']}"
    )
    print(f"Score: {result['score']}")
    print(f"\nLinkedIn invite:\n{result['linkedin_invite']}")
    print(f"\nEmail subject: {result['email_subject']}")
    print(f"Email body:\n{result['email_body']}")
    print(f"{'─' * 60}\n")

    log_path = Path(settings.output_dir) / "dry_run_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(result) + "\n")


def _send_linkedin(lead: ScoredLead, message: str):
    raise NotImplementedError("Live LinkedIn sending not implemented in PoC")


def _send_email(lead: ScoredLead, email):
    raise NotImplementedError("Live email sending not implemented in PoC")
