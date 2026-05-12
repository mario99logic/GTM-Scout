"""Holds the campaign-level context that flows through the pipeline."""

from dataclasses import dataclass


@dataclass
class CampaignContext:
    hunter_company: str        # The name of the company running the campaign.
    competitor_company: str    # The name of the competitor company whose users we're targeting.
    competitor_technology: str # The technology the competitor is known for.
