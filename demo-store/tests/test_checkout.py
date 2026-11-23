from decimal import Decimal

from src.checkout import calculate_total


def test_discount_code_is_applied_once():
    assert calculate_total(Decimal("100.00"), Decimal("10.00")) == Decimal("90.00")


def test_zero_discount_preserves_subtotal():
    assert calculate_total(Decimal("25.00"), Decimal("0.00")) == Decimal("25.00")
