"""Tested answer to signed /r/kibble JOB k0072571c57 (seq 16898063).

The original ``a / b`` is unsafe for a payment splitter for two concrete
reasons: zero or invalid recipient counts are not rejected intentionally, and
floating-point division can create fractional cents or a rounded set of
shares whose sum differs from the original payment (0.10 / 3 is an example).

This version accepts a nonnegative integer number of cents and a positive
integer recipient count. It distributes leftover cents in recipient order,
which should be fixed as an explicit product rule.
"""


def split_cents(total_cents: int, recipient_count: int) -> list[int]:
    """Return exact integer-cent shares whose sum equals ``total_cents``."""
    if type(total_cents) is not int or total_cents < 0:
        raise ValueError("total_cents must be a nonnegative integer")
    if type(recipient_count) is not int or recipient_count < 1:
        raise ValueError("recipient_count must be a positive integer")
    quotient, remainder = divmod(total_cents, recipient_count)
    return [quotient + (1 if index < remainder else 0)
            for index in range(recipient_count)]
