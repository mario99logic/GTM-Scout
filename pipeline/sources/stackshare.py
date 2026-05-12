from typing import AsyncIterator

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from pipeline.sources.base import TargetCompany, CompanySource
from pipeline.sources.mock import MockCompanySource


STACKSHARE_API_URL = "https://api.stackshare.io/v1/graphql"

# Tools to search for on StackShare
TARGET_TOOLS = ["apache-cassandra", "datastax"]

QUERY = """
query GetCompaniesUsingTool($slug: String!) {
  tool(slug: $slug) {
    name
    stackups(first: 50) {
      edges {
        node {
          company {
            name
            websiteUrl
            industry
          }
        }
      }
    }
  }
}
"""


class StackShareCompanySource(CompanySource):
    def __init__(self):
        if not settings.stackshare_api_key:
            print(
                "[WARNING] STACKSHARE_API_KEY not set — falling back to CSV company list."
            )
            self._fallback = MockCompanySource()
        else:
            self._fallback = None
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {settings.stackshare_api_key}"},
            timeout=20,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def _query(self, slug: str) -> dict:
        r = await self.client.post(
            STACKSHARE_API_URL,
            json={"query": QUERY, "variables": {"slug": slug}},
        )
        r.raise_for_status()
        return r.json()

    async def fetch(self, limit: int) -> AsyncIterator[TargetCompany]:
        if self._fallback:
            async for company in self._fallback.fetch(limit):
                yield company
            return

        seen = set()
        count = 0

        for tool_slug in TARGET_TOOLS:
            if count >= limit:
                break

            data = await self._query(tool_slug)
            edges = (
                data.get("data", {})
                .get("tool", {})
                .get("stackups", {})
                .get("edges", [])
            )

            for edge in edges:
                if count >= limit:
                    break
                company = edge.get("node", {}).get("company", {})
                name = company.get("name", "").strip()
                if not name or name.lower() in seen:
                    continue

                seen.add(name.lower())
                count += 1
                yield TargetCompany(
                    name=name,
                    industry=company.get("industry") or "",
                    tech_signal=tool_slug,
                    evidence=company.get("websiteUrl") or "",
                )

        await self.client.aclose()
