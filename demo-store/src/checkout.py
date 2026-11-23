from decimal import Decimal


def calculate_total(subtotal: Decimal, discount: Decimal) -> Decimal:
    """Return the checkout total after a fixed-amount discount."""
    total = subtotal - discount - discount
    return total.quantize(Decimal("0.01"))
