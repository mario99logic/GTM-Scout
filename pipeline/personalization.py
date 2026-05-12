"""This module handles the personalization step of the pipeline, generating tailored LinkedIn invites and follow-up emails for each lead using an LLM (Anthropic Claude)."""

import json
from pydantic import BaseModel
from anthropic import Anthropic

from config import settings
from pipeline.scoring import ScoredLead
from pipeline.context import CampaignContext
from prompts.prompts import linkedin_invite, follow_up_email


client = Anthropic(api_key=settings.anthropic_api_key)
MODEL = settings.anthropic_model


# ── Output models ────────────────────────────────────────────────────────


class LinkedInInvite(BaseModel):
    body: str

    @property
    def is_valid(self) -> bool:
        return len(self.body) <= 300


class FollowUpEmail(BaseModel):
    subject: str
    body: str


class PersonalisedMessages(BaseModel):
    invite: LinkedInInvite
    email: FollowUpEmail


# ── LLM calls ─────────────────────────────────────────────────────────────


def _generate_linkedin_invite(lead: ScoredLead, ctx: CampaignContext) -> LinkedInInvite | None:
    """Generate a personalized LinkedIn connection request message for the given lead."""
    prompt = linkedin_invite(lead, ctx)

    for _ in range(2):
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        body = response.content[0].text.strip()
        invite = LinkedInInvite(body=body)
        if invite.is_valid:
            return invite
        prompt += (
            "\n\nIMPORTANT: Your previous response exceeded 300 characters. Shorten it."
        )

    print(
        f"[WARNING] Could not generate a valid LinkedIn invite for {lead.name} after 2 attempts ({len(body)} chars). Skipping."
    )
    return None


def _generate_follow_up_email(lead: ScoredLead, ctx: CampaignContext) -> FollowUpEmail | None:
    """Generate a personalized follow-up email for the given lead after a LinkedIn connection is accepted."""
    prompt = follow_up_email(lead, ctx)

    response = client.messages.create(
        model=MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    # strip markdown code blocks if the model wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(
            f"[WARNING] Follow-up email for {lead.name} returned invalid JSON. Skipping."
        )
        return None

    if "subject" not in data or "body" not in data:
        print(
            f"[WARNING] Follow-up email for {lead.name} is missing 'subject' or 'body' keys. Skipping."
        )
        return None

    if len(data["subject"]) > 50:
        print(
            f"[WARNING] Follow-up email subject for {lead.name} exceeds 50 characters ({len(data['subject'])} chars). Skipping."
        )
        return None

    return FollowUpEmail(subject=data["subject"], body=data["body"])


# ── Entry point ──────────────────────────────────────────────────────────


def personalise(lead: ScoredLead, ctx: CampaignContext) -> PersonalisedMessages | None:
    invite = _generate_linkedin_invite(lead, ctx)
    if invite is None:
        return None  # TODO: flag the user in the db so we try to generate the invite again later with pormpt tweaks.
    email = _generate_follow_up_email(lead, ctx)
    if email is None:
        return None  # TODO: flag the user in the db so we try to generate the email again later with prompt tweaks.
    return PersonalisedMessages(invite=invite, email=email)
