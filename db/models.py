"""This module defines the SQLAlchemy models for the database, representing the core entities of the system: Report, Lead, and Message."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.session import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True)
    lead_source: Mapped[str] = mapped_column(String)
    total_found: Mapped[int] = mapped_column(Integer, default=0)
    total_qualified: Mapped[int] = mapped_column(Integer, default=0)
    total_selected: Mapped[int] = mapped_column(Integer, default=0)
    total_messaged: Mapped[int] = mapped_column(Integer, default=0)

    leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="report")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    report_id: Mapped[str] = mapped_column(String, ForeignKey("reports.id"))
    name: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    company: Mapped[str] = mapped_column(String)
    linkedin_url: Mapped[str] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(
        SAEnum("found", "qualified", "selected", "sent", "skipped", name="lead_status"),
        default="found",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    report: Mapped["Report"] = relationship("Report", back_populates="leads")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="lead")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    lead_id: Mapped[str] = mapped_column(String, ForeignKey("leads.id"))
    type: Mapped[str] = mapped_column(
        SAEnum("linkedin_invite", "follow_up_email", name="message_type"),
    )
    subject: Mapped[str | None] = mapped_column(String, nullable=True)
    body: Mapped[str] = mapped_column(Text)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    llm_model: Mapped[str] = mapped_column(String)
    prompt_version: Mapped[str] = mapped_column(String, default="v1")

    lead: Mapped["Lead"] = relationship("Lead", back_populates="messages")
