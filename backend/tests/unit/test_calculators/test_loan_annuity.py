import pytest

from app.core.calculators.loan_annuity import AnnuityLoanCalculator


class TestAnnuityLoanCalculator:
    def test_monthly_payment_calculation(self):
        calc = AnnuityLoanCalculator(principal=100000, annual_rate=12, term_months=12)
        result = calc.calculate()

        assert result["monthly_payment"] == pytest.approx(8884.88, abs=0.01)

    def test_schedule_has_correct_length(self):
        calc = AnnuityLoanCalculator(principal=100000, annual_rate=12, term_months=12)
        result = calc.calculate()

        assert len(result["schedule"]) == 12

    def test_final_balance_is_zero(self):
        calc = AnnuityLoanCalculator(principal=100000, annual_rate=12, term_months=12)
        result = calc.calculate()

        last_entry = result["schedule"][-1]
        assert last_entry["remaining_balance"] == pytest.approx(0, abs=0.5)

    def test_total_interest_is_positive(self):
        calc = AnnuityLoanCalculator(principal=100000, annual_rate=12, term_months=12)
        result = calc.calculate()

        assert result["total_interest"] > 0

    def test_total_payment_equals_monthly_times_term(self):
        calc = AnnuityLoanCalculator(principal=100000, annual_rate=12, term_months=12)
        result = calc.calculate()

        expected_total = result["monthly_payment"] * 12
        assert result["total_payment"] == pytest.approx(expected_total, abs=0.01)

    def test_zero_interest_rate_edge_case(self):
        calc = AnnuityLoanCalculator(principal=120000, annual_rate=0, term_months=12)
        result = calc.calculate()

        assert result["monthly_payment"] == pytest.approx(10000.0, abs=0.01)
        assert result["total_interest"] == pytest.approx(0.0, abs=0.01)

    def test_interest_decreases_each_month(self):
        calc = AnnuityLoanCalculator(principal=100000, annual_rate=12, term_months=12)
        result = calc.calculate()

        schedule = result["schedule"]
        for i in range(1, len(schedule)):
            assert schedule[i]["interest_part"] < schedule[i - 1]["interest_part"]

    def test_principal_part_increases_each_month(self):
        calc = AnnuityLoanCalculator(principal=100000, annual_rate=12, term_months=12)
        result = calc.calculate()

        schedule = result["schedule"]
        for i in range(1, len(schedule)):
            assert schedule[i]["principal_part"] > schedule[i - 1]["principal_part"]