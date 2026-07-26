from app.core.calculators.base import BaseCalculator


class DifferentiatedLoanCalculator(BaseCalculator):
    

    def __init__(self, principal: float, annual_rate: float, term_months: int):
        self.principal = principal
        self.annual_rate = annual_rate
        self.term_months = term_months

    def calculate(self) -> dict:
        monthly_rate = self.annual_rate / 12 / 100
        principal_part = self.principal / self.term_months  # однакова щомісяця

        schedule = []
        remaining_balance = self.principal
        total_payment = 0.0

        for month in range(1, self.term_months + 1):
            interest_part = remaining_balance * monthly_rate
            payment = principal_part + interest_part
            remaining_balance -= principal_part
            total_payment += payment

            schedule.append({
                "period": month,
                "payment": round(payment, 2),
                "principal_part": round(principal_part, 2),
                "interest_part": round(interest_part, 2),
                "remaining_balance": round(max(remaining_balance, 0), 2),
            })

        total_interest = total_payment - self.principal

        return {
            "first_payment": schedule[0]["payment"],
            "last_payment": schedule[-1]["payment"],
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2),
            "schedule": schedule,
        }