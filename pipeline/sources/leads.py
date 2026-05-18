from typing import AsyncIterator

from config import settings
from pipeline.sources.base import TargetCompany, RawLead, LeadSource


class CompositeLeadSource(LeadSource):
    """Fetches leads from Apollo and Proxycurl/LinkedIn, deduplicating by name+company."""

    async def fetch(
        self, companies: list[TargetCompany], limit: int
    ) -> AsyncIterator[RawLead]:
        from pipeline.sources.apollo import ApolloLeadSource
        from pipeline.sources.linkedin import LinkedInLeadSource

        seen: set[tuple[str, str]] = set()
        count = 0

        sources: list[LeadSource] = []
        if settings.apollo_api_key:
            sources.append(ApolloLeadSource())
        if settings.proxycurl_api_key:
            sources.append(LinkedInLeadSource())

        for source in sources:
            if count >= limit:
                break
            async for lead in source.fetch(companies=companies, limit=limit - count):
                key = (lead.name.lower(), lead.company.lower())
                if key in seen:
                    continue
                seen.add(key)
                count += 1
                yield lead
                if count >= limit:
                    break
