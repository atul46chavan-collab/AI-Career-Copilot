from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.student import Student
    from src.models.analysis import ResumeAnalysis


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    jd_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    extracted_data: Mapped[any] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        back_populates="job_descriptions"
    )

    analyses: Mapped[List["ResumeAnalysis"]] = relationship(
        back_populates="job_description",
        cascade="all, delete-orphan"
    )
