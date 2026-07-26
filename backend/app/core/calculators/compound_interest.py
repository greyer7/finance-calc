from app.core.calculators.base import BaseCalculator

FREQUENCY_TO_PERIODS_PER_YEAR = {
    "monthly": 12,
    "quarterly": 4,
    "annually": 1,
}


class CompoundInterestCalculator(BaseCalculator):
    

    def __init__(self, principal: float, annual_rate: float, term_months: int,
                 compounding_frequency: str = "monthly"):
        self.principal = principal
        self.annual_rate = annual_rate
        self.term_months = term_months
        self.compounding_frequency = compounding_frequency

    def calculate(self) -> dict:
        periods_per_year = FREQUENCY_TO_PERIODS_PER_YEAR[self.compounding_frequency]
        period_rate = self.annual_rate / 100 / periods_per_year
        total_periods = round(self.term_months / 12 * periods_per_year)

        schedule = []
        balance = self.principal
        months_per_period = 12 / periods_per_year

        for period in range(1, total_periods + 1):
            balance *= (1 + period_rate)

            schedule.append({
                "period": round(period * months_per_period),  
                "remaining_balance": round(balance, 2),
            })

        final_amount = balance
        total_interest_earned = final_amount - self.principal

        return {
            "final_amount": round(final_amount, 2),
            "total_interest_earned": round(total_interest_earned, 2),
            "schedule": schedule,
        }