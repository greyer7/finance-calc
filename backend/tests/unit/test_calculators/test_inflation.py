import pytest

from app.core.calculators.inflation import InflationCalculator


class TestInflationCalculator:
    def test_adjusted_value_is_less_than_original(self):
        calc = InflationCalculator(amount=10000, annual_inflation_rate=8, term_years=5)
        result = calc.calculate()

        assert result["adjusted_value"] < 10000

    def test_adjusted_value_calculation(self):
        calc = InflationCalculator(amount=10000, annual_inflation_rate=8, term_years=5)
        result = calc.calculate()

        assert result["adjusted_value"] == pytest.approx(6805.83, abs=0.5)

    def test_purchasing_power_loss_percentage(self):
        calc = InflationCalculator(amount=10000, annual_inflation_rate=8, term_years=5)
        result = calc.calculate()

        assert result["purchasing_power_loss"] == pytest.approx(31.94, abs=0.5)

    def test_yearly_breakdown_has_correct_length(self):
        calc = InflationCalculator(amount=10000, annual_inflation_rate=8, term_years=5)
        result = calc.calculate()

        assert len(result["yearly_breakdown"]) == 5

    def test_value_decreases_each_year(self):
        calc = InflationCalculator(amount=10000, annual_inflation_rate=8, term_years=5)
        result = calc.calculate()

        breakdown = result["yearly_breakdown"]
        for i in range(1, len(breakdown)):
            assert breakdown[i]["remaining_balance"] < breakdown[i - 1]["remaining_balance"]

    def test_zero_inflation_rate_keeps_value_unchanged(self):
        calc = InflationCalculator(amount=10000, annual_inflation_rate=0, term_years=5)
        result = calc.calculate()

        assert result["adjusted_value"] == pytest.approx(10000, abs=0.01)
        assert result["purchasing_power_loss"] == pytest.approx(0, abs=0.01)

    def test_higher_inflation_causes_greater_loss(self):
        low_inflation = InflationCalculator(amount=10000, annual_inflation_rate=3, term_years=5).calculate()
        high_inflation = InflationCalculator(amount=10000, annual_inflation_rate=15, term_years=5).calculate()

        assert high_inflation["purchasing_power_loss"] > low_inflation["purchasing_power_loss"]