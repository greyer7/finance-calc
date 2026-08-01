from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_current_verified_user
from app.models.user import User
from app.services.calculation_service import CalculationService
from app.schemas.calculator import (
    LoanRequest,
    LoanResponse,
    DifferentiatedLoanResponse,
    CompoundInterestRequest,
    CompoundInterestResponse,
    InflationRequest,
    InflationResponse,
    CalculationHistoryItem,
)

router = APIRouter(prefix="/calculate", tags=["calculators"])


@router.post("/loan/annuity", response_model=LoanResponse)
async def calculate_loan_annuity(
    data: LoanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    calc_service = CalculationService(db)
    return await calc_service.calculate_loan_annuity(current_user.id, data)


@router.post("/loan/differentiated", response_model=DifferentiatedLoanResponse)
async def calculate_loan_differentiated(
    data: LoanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    calc_service = CalculationService(db)
    return await calc_service.calculate_loan_differentiated(current_user.id, data)


@router.post("/deposit", response_model=CompoundInterestResponse)
async def calculate_deposit(
    data: CompoundInterestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    calc_service = CalculationService(db)
    return await calc_service.calculate_compound_interest(current_user.id, data)


@router.post("/inflation", response_model=InflationResponse)
async def calculate_inflation(
    data: InflationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    calc_service = CalculationService(db)
    return await calc_service.calculate_inflation(current_user.id, data)


@router.get("/history", response_model=List[CalculationHistoryItem])
async def get_calculation_history(
    calculation_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    calc_service = CalculationService(db)
    history = await calc_service.get_user_history(
        user_id=current_user.id,
        calculation_type=calculation_type,
        limit=limit,
        offset=offset,
    )
    return history


@router.delete("/history/{calculation_id}", status_code=204)
async def delete_calculation(
    calculation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    calc_service = CalculationService(db)
    deleted = await calc_service.delete_calculation(calculation_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return None