from typing import Optional
import uuid

from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from app.models.models import Stage, Question


class StageQuestion(Base):
    __tablename__ = "stage_question"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stage.id"), nullable=False)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("question.id"), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    stage: Mapped["Stage"] = relationship(back_populates="stage_questions")
    question: Mapped["Question"] = relationship(back_populates="stage_questions")