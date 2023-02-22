num = 123

# Test error message for Python <= 3.9, since the type union form is only
# supported in Python 3.10+

_ = isinstance(num, float) or isinstance(num, int)
