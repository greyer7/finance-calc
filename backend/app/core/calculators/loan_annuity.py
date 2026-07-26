from app.core.calculators.base import BaseCalculator


class AnnuityLoanCalculator(BaseCalculator):
    

    def __init__(self, principal: float, annual_rate: float, term_months: int):
        self.principal = principal
        self.annual_rate = annual_rate
        self.term_months = term_months

    def calculate(self) -> dict:
        monthly_rate = self.annual_rate / 12 / 100

        if monthly_rate == 0:
            monthly_payment = self.principal / self.term_months
        else:
            monthly_payment = self.principal * (
                monthly_rate * (1 + monthly_rate) ** self.term_months
            ) / (
                (1 + monthly_rate) ** self.term_months - 1
            )

        schedule = self._build_schedule(monthly_payment, monthly_rate)

        total_payment = monthly_payment * self.term_months
        total_interest = total_payment - self.principal

        return {
            "monthly_payment": round(monthly_payment, 2),
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2),
            "schedule": schedule,
        }

    def _build_schedule(self, monthly_payment: float, monthly_rate: float) -> list[dict]:
        schedule = []
        remaining_balance = self.principal

        for month in range(1, self.term_months + 1):
            interest_part = remaining_balance * monthly_rate
            principal_part = monthly_payment - interest_part
            remaining_balance -= principal_part

            schedule.append({
                "period": month,
                "payment": round(monthly_payment, 2),
                "principal_part": round(principal_part, 2),
                "interest_part": round(interest_part, 2),
                "remaining_balance": round(max(remaining_balance, 0), 2),
            })

        return schedule