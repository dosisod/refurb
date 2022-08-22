# this will match

if not not False:
    pass

value = 123
if not not value:
    pass


# these will not match

if bool(123):
    pass

if not False:
    pass
