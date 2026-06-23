from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.resume import Resume
    from src.models.job_description import JobDescription


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False
    )

    # Job description can be null if it's a general resume review without a specific target job.
    jd_id: Mapped[int | None] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="SET NULL"),
        nullable=True
    )

    strengths: Mapped[Any] = mapped_column(
        JSON,
        nullable=False
    )

    weaknesses: Mapped[Any] = mapped_column(
        JSON,
        nullable=False
    )

    suggestions: Mapped[Any] = mapped_column(
        JSON,
        nullable=False
    )

    skills_extracted: Mapped[Any] = mapped_column(
        JSON,
        nullable=False
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    resume: Mapped["Resume"] = relationship(
        back_populates="analyses"
    )

    job_description: Mapped["JobDescription | None"] = relationship(
        back_populates="analyses"
    )
