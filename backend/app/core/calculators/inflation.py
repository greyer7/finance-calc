from app.core.calculators.base import BaseCalculator


class InflationCalculator(BaseCalculator):
    

    def __init__(self, amount: float, annual_inflation_rate: float, term_years: int):
        self.amount = amount
        self.annual_inflation_rate = annual_inflation_rate
        self.term_years = term_years

    def calculate(self) -> dict:
        rate = self.annual_inflation_rate / 100

        yearly_breakdown = []
        adjusted_value = self.amount

        for year in range(1, self.term_years + 1):
            adjusted_value /= (1 + rate)  
            yearly_breakdown.append({
                "period": year,
                "remaining_balance": round(adjusted_value, 2),
            })

        purchasing_power_loss = (1 - adjusted_value / self.amount) * 100

        return {
            "adjusted_value": round(adjusted_value, 2),
            "purchasing_power_loss": round(purchasing_power_loss, 2),
            "yearly_breakdown": yearly_breakdown,
        }