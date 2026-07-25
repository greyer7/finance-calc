from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Calculation(Base):
    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    calculation_type: Mapped[str] = mapped_column(String(50), nullable=False)  
    # --- Вхідні параметри розрахунку ---
    principal: Mapped[float] = mapped_column(Float, nullable=False)          
    interest_rate: Mapped[float] = mapped_column(Float, nullable=False)      
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)       
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    
    result: Mapped[dict] = mapped_column(JSON, nullable=False)

    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="calculations")

    def __repr__(self) -> str:
        return f"<Calculation id={self.id} type={self.calculation_type} user_id={self.user_id}>"