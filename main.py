"""GTM Hunter — automated competitor user outreach.
This script implements the main pipeline for discovering target companies and leads, generating personalized messages, and triggering outreach actions."""

import asyncio
import click

from config import settings
from db.session import init_db
from pipeline.context import CampaignContext
from pipeline.sources import get_company_source, get_lead_source
from pipeline.scoring import process
from pipeline.personalization import personalise
from pipeline.trigger import trigger
from pipeline.storage import (
    create_report,
    save_lead,
    save_messages,
    update_lead_status,
    finish_report,
)


@click.group()
def cli():
    """GTM Hunter — automated competitor user outreach."""


@cli.command()
@click.option(
    "--mock", is_flag=True, default=False, help="Use mock data instead of real APIs."
)
@click.option("--dry-run/--live", default=settings.dry_run)
@click.option("--max-companies", default=10, type=int)
@click.option("--max-leads", default=settings.max_leads, type=int)
@click.option("--hunter-company", required=True, help="Your company name.")
@click.option("--competitor-company", required=True, help="The competitor company to target.")
@click.option("--competitor-technology", required=True, help="The technology the competitor is known for.")
def run(mock, dry_run, max_companies, max_leads, hunter_company, competitor_company, competitor_technology):
    """Run the full pipeline."""
    ctx = CampaignContext(
        hunter_company=hunter_company,
        competitor_company=competitor_company,
        competitor_technology=competitor_technology,
    )
    asyncio.run(_pipeline(mock, dry_run, max_companies, max_leads, ctx))


async def _pipeline(mock: bool, dry_run: bool, max_companies: int, max_leads: int, ctx: CampaignContext):
    init_db()

    report_id = create_report(lead_source="mock" if mock else "api+linkedin")
    stats = {
        "total_found": 0,
        "total_qualified": 0,
        "total_selected": 0,
        "total_messaged": 0,
    }

    print("\nGTM Hunter")
    print(f"Hunter company : {ctx.hunter_company}")
    print(f"Targeting      : {ctx.competitor_company} ({ctx.competitor_technology}) users")
    print(f"Mode           : {'mock' if mock else 'live'}")
    print(f"Dry run        : {dry_run}")
    print(f"Max companies  : {max_companies} | Max leads: {max_leads}\n")

    # ── Step 1: Company discovery ─────────────────────────────────────────
    # We could also add a step here to enrich the company data with info like size, funding, tech stack etc.
    # Using sources like Clearbit or Apollo. This would allow for better lead scoring and personalization later on.
    company_source = get_company_source(mock=mock)
    companies = []
    async for company in company_source.fetch(limit=max_companies):
        companies.append(company)
        print(f"[COMPANY] {company.name} ({company.tech_signal})")

    print(f"\nFound {len(companies)} target companies.\n")

    if not companies:
        print("[ERROR] No target companies found. Exiting.")
        return

    # ── Step 2: Lead discovery ────────────────────────────────────────────
    # For each target company, find relevant leads (e.g. engineers, architects, managers) using the specified lead source.
    # Then filter and score the leads based on relevance, seniority, and potential fit for the hunter company.
    lead_source = get_lead_source(mock=mock)

    async for raw in lead_source.fetch(companies=companies, limit=max_leads):
        stats["total_found"] += 1

        # Stage 1 — filter + score.
        scored, reason = process(raw)
        if scored is None:
            print(f"[SKIP] {raw.name} — {reason}")
            continue

        if scored.score < settings.score_threshold:
            print(f"[SKIP] {raw.name} — score too low ({scored.score})")
            continue

        stats["total_qualified"] += 1

        # Save lead to DB after it passes the filter.
        lead_id = save_lead(report_id, scored)

        # Stage 2 — generate messages.
        messages = personalise(scored, ctx)
        if messages is None:
            update_lead_status(lead_id, "skipped")
            continue

        stats["total_selected"] += 1

        # Stage 3 — trigger (dry-run log or live send).
        trigger(scored, messages, dry_run=dry_run)
        update_lead_status(lead_id, "sent" if not dry_run else "selected")

        # Save messages to DB after trigger fires.
        save_messages(lead_id, messages)
        stats["total_messaged"] += 1

    # ── Finalize ──────────────────────────────────────────────────────────
    finish_report(report_id, stats)

    print(
        f"\nDone — found={stats['total_found']} qualified={stats['total_qualified']} messaged={stats['total_messaged']}"
    )


if __name__ == "__main__":
    cli()
