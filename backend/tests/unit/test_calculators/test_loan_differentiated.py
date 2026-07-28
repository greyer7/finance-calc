import pytest

from app.core.calculators.loan_differentiated import DifferentiatedLoanCalculator


class TestDifferentiatedLoanCalculator:
    def test_first_payment_is_larger_than_last(self):
        calc = DifferentiatedLoanCalculator(principal=100000, annual_rate=12, term_months=12)
        result = calc.calculate()

        assert result["first_payment"] > result["last_payment"]

    def test_principal_part_is_constant(self):
        calc = DifferentiatedLoanCalculator(principal=120000, annual_rate=12, term_months=12)
        result = calc.calculate()

        schedule = result["schedule"]
        expected_principal_part = 120000 / 12

        for entry in schedule:
            assert entry["principal_part"] == pytest.approx(expected_principal_part, abs=0.01)

    def test_payment_decreases_each_month(self):
        calc = DifferentiatedLoanCalculator(principal=100000, annual_rate=12, term_months=12)
        result = calc.calculate()

        schedule = result["schedule"]
        for i in range(1, len(schedule)):
            assert schedule[i]["payment"] < schedule[i - 1]["payment"]

    def test_final_balance_is_zero(self):
        calc = DifferentiatedLoanCalculator(principal=100000, annual_rate=12, term_months=12)
        result = calc.calculate()

        assert result["schedule"][-1]["remaining_balance"] == pytest.approx(0, abs=0.5)

    def test_differentiated_has_less_total_interest_than_annuity(self):
        from app.core.calculators.loan_annuity import AnnuityLoanCalculator

        annuity_result = AnnuityLoanCalculator(principal=100000, annual_rate=12, term_months=12).calculate()
        differentiated_result = DifferentiatedLoanCalculator(principal=100000, annual_rate=12, term_months=12).calculate()

        assert differentiated_result["total_interest"] < annuity_result["total_interest"]