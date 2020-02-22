def div_ceil(div_ident: int, divisor: int) -> int:
    """Integer division with rounding up"""

    q, r = divmod(div_ident, divisor)
    return q + bool(r)
