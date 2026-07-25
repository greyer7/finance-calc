from typing import Optional, List, Literal

from pydantic import BaseModel, Field


#  Спільні "будівельні блоки"

class ScheduleEntry(BaseModel):
    """Один рядок графіка платежів/нарахувань (один місяць або рік)."""
    period: int                     
    payment: Optional[float] = None  
    principal_part: Optional[float] = None   
    interest_part: Optional[float] = None    
    remaining_balance: float         

#  Кредит — ануїтетний платіж

class LoanRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Сума кредиту")
    annual_rate: float = Field(..., gt=0, le=100, description="Річна процентна ставка, %")
    term_months: int = Field(..., gt=0, le=600, description="Строк кредиту в місяцях")
    currency: str = Field(default="USD", min_length=3, max_length=3)


class LoanResponse(BaseModel):
    monthly_payment: float
    total_payment: float             
    total_interest: float            
    schedule: List[ScheduleEntry]


#  Кредит — диференційований платіж

class DifferentiatedLoanResponse(BaseModel):
    first_payment: float             
    last_payment: float
    total_payment: float
    total_interest: float
    schedule: List[ScheduleEntry]


#  Складний відсоток (депозит)

class CompoundInterestRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Початкова сума депозиту")
    annual_rate: float = Field(..., gt=0, le=100, description="Річна ставка, %")
    term_months: int = Field(..., gt=0, le=600, description="Строк у місяцях")
    compounding_frequency: Literal["monthly", "quarterly", "annually"] = "monthly"
    currency: str = Field(default="USD", min_length=3, max_length=3)


class CompoundInterestResponse(BaseModel):
    final_amount: float             
    total_interest_earned: float     
    schedule: List[ScheduleEntry]


#  Інфляція

class InflationRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Початкова сума")
    annual_inflation_rate: float = Field(..., gt=0, le=100, description="Річний рівень інфляції, %")
    term_years: int = Field(..., gt=0, le=50, description="Строк у роках")
    currency: str = Field(default="USD", min_length=3, max_length=3)


class InflationResponse(BaseModel):
    adjusted_value: float            
    purchasing_power_loss: float     
    yearly_breakdown: List[ScheduleEntry]