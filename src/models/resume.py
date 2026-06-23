from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.student import Student
    from src.models.analysis import ResumeAnalysis


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False
    )

    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        back_populates="resumes"
    )

    analyses: Mapped[List["ResumeAnalysis"]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan"
    )
