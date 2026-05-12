from typing import AsyncIterator

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from pipeline.sources.base import TargetCompany, CompanySource


GITHUB_BASE_URL = "https://api.github.com/"

GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# Search queries to find orgs using Cassandra/DataStax
ORG_SEARCH_QUERIES = [
    "cassandra in:description type:org",
    "datastax in:description type:org",
]

# Code search to find orgs whose repos import Cassandra drivers
CODE_SEARCH_QUERIES = [
    ("cassandra-driver", "python"),
    ("com.datastax.cassandra", "java"),
    ("gocql", "go"),
]


class GitHubCompanySource(CompanySource):
    def __init__(self):
        headers = GITHUB_HEADERS.copy()
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        self.client = httpx.AsyncClient(
            base_url=GITHUB_BASE_URL, headers=headers, timeout=15
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def _get(self, url: str, params: dict = None) -> dict:
        r = await self.client.get(url, params=params)
        r.raise_for_status()
        return r.json()

    async def fetch(self, limit: int) -> AsyncIterator[TargetCompany]:
        seen = set()
        count = 0

        # 1. Orgs whose description mentions Cassandra/DataStax.
        for query in ORG_SEARCH_QUERIES:
            if count >= limit:
                break
            data = await self._get("search/users", params={"q": query, "per_page": 30})
            for item in data.get("items", []):
                if count >= limit:
                    break
                name = item.get("login", "")
                if name.lower() in seen:
                    continue
                seen.add(name.lower())
                count += 1
                yield TargetCompany(
                    name=name,
                    tech_signal="cassandra" if "cassandra" in query else "datastax",
                    evidence=item.get("html_url", ""),
                )

        # 2. Orgs whose repos import Cassandra drivers.
        for query, language in CODE_SEARCH_QUERIES:
            if count >= limit:
                break
            data = await self._get(
                "search/code",
                params={"q": f"{query} language:{language}", "per_page": 30},
            )
            for item in data.get("items", []):
                if count >= limit:
                    break
                owner = item.get("repository", {}).get("owner", {})
                if owner.get("type") != "Organization":
                    continue
                name = owner.get("login", "")
                if not name or name.lower() in seen:
                    continue
                seen.add(name.lower())
                count += 1
                yield TargetCompany(
                    name=name,
                    tech_signal=query,
                    evidence=item.get("repository", {}).get("html_url", ""),
                )

        await self.client.aclose()
