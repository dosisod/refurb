import decimal
from decimal import Decimal

# these should match

_ = Decimal("0")
_ = Decimal("+0")
_ = Decimal("-0")
_ = Decimal("-1234")
_ = Decimal("1234")
_ = Decimal("01234")
_ = Decimal("\r\n\r 1234")
_ = Decimal(float("Infinity"))
_ = Decimal(float("-Infinity"))
_ = Decimal(float("inf"))
_ = Decimal(float("-inf"))
_ = Decimal(float("-INF"))
_ = Decimal(float("NaN"))
_ = Decimal(float("nan"))
_ = decimal.Decimal("0")
_ = decimal.Decimal(float("nan"))


# these should not

_ = Decimal("3.14")
_ = Decimal("10e3")
_ = Decimal(float("3.14"))
_ = Decimal("0x123")
