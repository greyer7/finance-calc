import pytest

from app.core.calculators.compound_interest import CompoundInterestCalculator


class TestCompoundInterestCalculator:
    def test_final_amount_is_greater_than_principal(self):
        calc = CompoundInterestCalculator(
            principal=100000, annual_rate=12, term_months=12, compounding_frequency="monthly"
        )
        result = calc.calculate()

        assert result["final_amount"] > 100000

    def test_final_amount_calculation_monthly(self):
        calc = CompoundInterestCalculator(
            principal=100000, annual_rate=12, term_months=12, compounding_frequency="monthly"
        )
        result = calc.calculate()

        assert result["final_amount"] == pytest.approx(112682.50, abs=0.5)

    def test_monthly_compounding_yields_more_than_annual(self):
        monthly_result = CompoundInterestCalculator(
            principal=100000, annual_rate=12, term_months=12, compounding_frequency="monthly"
        ).calculate()

        annual_result = CompoundInterestCalculator(
            principal=100000, annual_rate=12, term_months=12, compounding_frequency="annually"
        ).calculate()

        assert monthly_result["final_amount"] > annual_result["final_amount"]

    def test_total_interest_earned_equals_difference(self):
        calc = CompoundInterestCalculator(
            principal=100000, annual_rate=12, term_months=12, compounding_frequency="monthly"
        )
        result = calc.calculate()

        expected_interest = result["final_amount"] - 100000
        assert result["total_interest_earned"] == pytest.approx(expected_interest, abs=0.01)

    def test_balance_grows_each_period(self):
        calc = CompoundInterestCalculator(
            principal=100000, annual_rate=12, term_months=12, compounding_frequency="monthly"
        )
        result = calc.calculate()

        schedule = result["schedule"]
        for i in range(1, len(schedule)):
            assert schedule[i]["remaining_balance"] > schedule[i - 1]["remaining_balance"]

    def test_quarterly_schedule_period_mapping(self):
        calc = CompoundInterestCalculator(
            principal=100000, annual_rate=12, term_months=12, compounding_frequency="quarterly"
        )
        result = calc.calculate()

        periods = [entry["period"] for entry in result["schedule"]]
        assert periods == [3, 6, 9, 12]

    def test_zero_interest_rate(self):
        calc = CompoundInterestCalculator(
            principal=50000, annual_rate=0, term_months=12, compounding_frequency="monthly"
        )
        result = calc.calculate()

        assert result["final_amount"] == pytest.approx(50000, abs=0.01)
        assert result["total_interest_earned"] == pytest.approx(0, abs=0.01)