"""Apollo.io lead source implementation."""
from typing import AsyncIterator

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from pipeline.sources.base import TargetCompany, RawLead, LeadSource

_TITLES = ["engineer", "architect", "developer", "platform", "infrastructure"]


class ApolloLeadSource(LeadSource):
    BASE_URL = "https://api.apollo.io/v1/mixed_people/search"

    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": settings.apollo_api_key,
            },
            timeout=20,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def _search(self, payload: dict) -> dict:
        r = await self.client.post(self.BASE_URL, json=payload)
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
                    "organization_names": [company.name],
                    "person_titles": _TITLES,
                    "page": 1,
                    "per_page": min(limit - count, 10),
                }
            )

            for person in data.get("people", []):
                if count >= limit:
                    break

                email = person.get("email") or ""
                notes = person.get("headline") or ""
                if email:
                    notes = f"email:{email} {notes}".strip()

                yield RawLead(
                    name=person.get("name", ""),
                    title=person.get("title", ""),
                    company=company.name,
                    linkedin_url=person.get("linkedin_url", "") or "",
                    source="apollo",
                    notes=notes,
                )
                count += 1

        await self.client.aclose()
