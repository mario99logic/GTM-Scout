from typing import AsyncIterator

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from pipeline.sources.base import TargetCompany, RawLead, LeadSource


class LinkedInLeadSource(LeadSource):
    BASE_URL = "https://nubela.co/proxycurl/api/v2/search/person"

    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {settings.proxycurl_api_key}"},
            timeout=20,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def _search(self, params: dict) -> dict:
        r = await self.client.get(self.BASE_URL, params=params)
        r.raise_for_status()
        return r.json()

    async def fetch(
        self, companies: list[TargetCompany], limit: int
    ) -> AsyncIterator[RawLead]:
        count = 0

        for company in companies:
            if count >= limit:
                break

            data = await self._search(
                {
                    "current_company_name": company.name,
                    "headline": "engineer OR architect OR developer OR platform OR infrastructure",
                    "country": "US",
                    "page_size": min(limit, 10),
                }
            )

            for item in data.get("results", []):
                if count >= limit:
                    break
                profile = item.get("person", {})
                yield RawLead(
                    name=profile.get("full_name", ""),
                    title=profile.get("headline", ""),
                    company=company.name,
                    linkedin_url=profile.get("linkedin_profile_url", ""),
                    source="linkedin",
                    notes=profile.get("summary", ""),
                )
                count += 1

        await self.client.aclose()
