import decimal
import fractions
from decimal import Decimal
from fractions import Fraction

# these should match

_ = Decimal.from_float(123)
_ = Fraction.from_float(123)
_ = Fraction.from_decimal(Decimal(123))
_ = decimal.Decimal.from_float(123)
_ = fractions.Fraction.from_float(123)


# these should not

_ = Decimal(123)
_ = Fraction(123)

_ = Decimal.from_float(123, 456)  # type: ignore
_ = Fraction.from_float(123, 456)  # type: ignore
_ = Decimal.from_decimal(123)  # type: ignore
