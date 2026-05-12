from typing import AsyncIterator

from pipeline.sources.base import TargetCompany, CompanySource as BaseCompanySource
from pipeline.sources.stackshare import StackShareCompanySource
from pipeline.sources.github_orgs import GitHubCompanySource


class APICompanySource(BaseCompanySource):
    """Fetches companies from both StackShare and GitHub, deduplicates by name."""

    def __init__(self):
        self.stackshare = StackShareCompanySource()
        self.github = GitHubCompanySource()

    async def fetch(self, limit: int) -> AsyncIterator[TargetCompany]:
        seen = set()
        count = 0

        async for company in self.stackshare.fetch(limit=limit):
            if company.name.lower() not in seen:
                seen.add(company.name.lower())
                count += 1
                yield company

        async for company in self.github.fetch(limit=limit):
            if count >= limit:
                break
            if company.name.lower() not in seen:
                seen.add(company.name.lower())
                count += 1
                yield company
