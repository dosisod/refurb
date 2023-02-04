# these should match

_ = "0123456789"
_ = "01234567"
_ = "0123456789abcdefABCDEF"
_ = "abcdefghijklmnopqrstuvwxyz"
_ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_ = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_ = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
_ = " \t\n\r\v\f"

_ = "" in "1234567890"
_ = "" in "12345670"


# these should not

_ = "1234567890"
_ = "1234"
_ = "" in "1234"
