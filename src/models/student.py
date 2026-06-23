from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.resume import Resume
    from src.models.job_description import JobDescription


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    course: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    resumes: Mapped[List["Resume"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan"
    )

    job_descriptions: Mapped[List["JobDescription"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan"
    )