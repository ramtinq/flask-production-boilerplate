from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, JSON
from typing import Any

from app.models import BaseModel

class CalculationResult(BaseModel):
    __tablename__ = 'calculation_results'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    data: Mapped[Any] = mapped_column(JSON, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="results")