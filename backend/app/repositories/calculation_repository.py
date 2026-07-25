from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calculation import Calculation


class CalculationRepository:
    

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, calculation_id: int) -> Optional[Calculation]:
        result = await self.db.execute(
            select(Calculation).where(Calculation.id == calculation_id)
        )
        return result.scalar_one_or_none()

    async def get_all_for_user(
        self,
        user_id: int,
        calculation_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Calculation]:
        query = select(Calculation).where(Calculation.user_id == user_id)

        if calculation_type is not None:
            query = query.where(Calculation.calculation_type == calculation_type)

        query = query.order_by(Calculation.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        user_id: int,
        calculation_type: str,
        principal: float,
        interest_rate: float,
        term_months: int,
        currency: str,
        result: dict,
        title: Optional[str] = None,
    ) -> Calculation:
        calculation = Calculation(
            user_id=user_id,
            calculation_type=calculation_type,
            principal=principal,
            interest_rate=interest_rate,
            term_months=term_months,
            currency=currency,
            result=result,
            title=title,
        )
        self.db.add(calculation)
        await self.db.commit()
        await self.db.refresh(calculation)
        return calculation

    async def delete_by_id(self, calculation_id: int, user_id: int) -> bool:
        
        result = await self.db.execute(
            delete(Calculation).where(
                Calculation.id == calculation_id,
                Calculation.user_id == user_id,
            )
        )
        await self.db.commit()
        return result.rowcount > 0