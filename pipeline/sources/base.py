from abc import ABC, abstractmethod
from typing import AsyncIterator

from pydantic import BaseModel


class TargetCompany(BaseModel):
    name: str
    industry: str = ""
    tech_signal: str = ""  # e.g. "cassandra", "datastax", "cassandra+datastax"
    evidence: str = ""  # public source URL confirming Cassandra usage


class RawLead(BaseModel):
    name: str
    title: str
    company: str
    linkedin_url: str
    source: str
    notes: str = ""


class CompanySource(ABC):
    @abstractmethod
    async def fetch(self, limit: int) -> AsyncIterator[TargetCompany]: ...


class LeadSource(ABC):
    @abstractmethod
    async def fetch(
        self, companies: list[TargetCompany], limit: int
    ) -> AsyncIterator[RawLead]: ...


def get_company_source(mock: bool = False) -> CompanySource:
    from pipeline.sources.mock import MockCompanySource
    from pipeline.sources.companies import APICompanySource

    return MockCompanySource() if mock else APICompanySource()


def get_lead_source(mock: bool = False) -> LeadSource:
    from pipeline.sources.mock import MockLeadSource
    from pipeline.sources.linkedin import LinkedInLeadSource

    return MockLeadSource() if mock else LinkedInLeadSource()
