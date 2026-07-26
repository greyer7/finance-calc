from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calculation import Calculation
from app.repositories.calculation_repository import CalculationRepository
from app.core.calculators.loan_annuity import AnnuityLoanCalculator
from app.core.calculators.loan_differentiated import DifferentiatedLoanCalculator
from app.core.calculators.compound_interest import CompoundInterestCalculator
from app.core.calculators.inflation import InflationCalculator
from app.schemas.calculator import (
    LoanRequest,
    LoanResponse,
    DifferentiatedLoanResponse,
    CompoundInterestRequest,
    CompoundInterestResponse,
    InflationRequest,
    InflationResponse,
)


class CalculationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.calc_repo = CalculationRepository(db)

    #  Кредит — ануїтет

    async def calculate_loan_annuity(self, user_id: int, data: LoanRequest) -> LoanResponse:
        calculator = AnnuityLoanCalculator(
            principal=data.principal,
            annual_rate=data.annual_rate,
            term_months=data.term_months,
        )
        result = calculator.calculate()

        await self.calc_repo.create(
            user_id=user_id,
            calculation_type="loan_annuity",
            principal=data.principal,
            interest_rate=data.annual_rate,
            term_months=data.term_months,
            currency=data.currency,
            result=result,
        )

        return LoanResponse(**result)

    #  Кредит — диференційований платіж

    async def calculate_loan_differentiated(self, user_id: int, data: LoanRequest) -> DifferentiatedLoanResponse:
        calculator = DifferentiatedLoanCalculator(
            principal=data.principal,
            annual_rate=data.annual_rate,
            term_months=data.term_months,
        )
        result = calculator.calculate()

        await self.calc_repo.create(
            user_id=user_id,
            calculation_type="loan_differentiated",
            principal=data.principal,
            interest_rate=data.annual_rate,
            term_months=data.term_months,
            currency=data.currency,
            result=result,
        )

        return DifferentiatedLoanResponse(**result)

    #  Складний відсоток (депозит)

    async def calculate_compound_interest(self, user_id: int, data: CompoundInterestRequest) -> CompoundInterestResponse:
        calculator = CompoundInterestCalculator(
            principal=data.principal,
            annual_rate=data.annual_rate,
            term_months=data.term_months,
            compounding_frequency=data.compounding_frequency,
        )
        result = calculator.calculate()

        await self.calc_repo.create(
            user_id=user_id,
            calculation_type="compound_interest",
            principal=data.principal,
            interest_rate=data.annual_rate,
            term_months=data.term_months,
            currency=data.currency,
            result=result,
        )

        return CompoundInterestResponse(**result)

    #  Інфляція

    async def calculate_inflation(self, user_id: int, data: InflationRequest) -> InflationResponse:
        calculator = InflationCalculator(
            amount=data.amount,
            annual_inflation_rate=data.annual_inflation_rate,
            term_years=data.term_years,
        )
        result = calculator.calculate()

        await self.calc_repo.create(
            user_id=user_id,
            calculation_type="inflation",
            principal=data.amount,
            interest_rate=data.annual_inflation_rate,
            term_months=data.term_years * 12,  
            currency=data.currency,
            result=result,
        )

        return InflationResponse(**result)

    #  Історія розрахунків

    async def get_user_history(
        self,
        user_id: int,
        calculation_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Calculation]:
        return await self.calc_repo.get_all_for_user(
            user_id=user_id,
            calculation_type=calculation_type,
            limit=limit,
            offset=offset,
        )

    async def delete_calculation(self, calculation_id: int, user_id: int) -> bool:
        return await self.calc_repo.delete_by_id(calculation_id, user_id)