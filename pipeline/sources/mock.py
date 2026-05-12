import csv
from typing import AsyncIterator

from pipeline.sources.base import TargetCompany, RawLead, CompanySource, LeadSource


class MockCompanySource(CompanySource):
    def __init__(self, path: str = "data/target_companies.csv"):
        self.path = path

    async def fetch(self, limit: int) -> AsyncIterator[TargetCompany]:
        with open(self.path) as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                yield TargetCompany(
                    name=row["company_name"],
                    industry=row.get("industry", ""),
                    tech_signal=row.get("tech_signal", ""),
                    evidence=row.get("evidence", ""),
                )


class MockLeadSource(LeadSource):
    def __init__(self, path: str = "data/seed_leads.csv"):
        self.path = path

    async def fetch(
        self, companies: list[TargetCompany], limit: int
    ) -> AsyncIterator[RawLead]:
        company_names = {c.name.lower() for c in companies}
        count = 0

        with open(self.path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if count >= limit:
                    break
                if row["company"].lower() not in company_names:
                    continue
                yield RawLead(
                    name=row["name"],
                    title=row["title"],
                    company=row["company"],
                    linkedin_url=row["linkedin_url"],
                    source="mock",
                    notes=row.get("notes", ""),
                )
                count += 1
