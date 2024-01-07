l = []

# these should match

l = sorted(l)
l = sorted(l, key=lambda x: x > 0)
l = sorted(l, reverse=True)
l = sorted(l, key=lambda x: x > 0, reverse=True)


# these should not

l2 = sorted(l)
l2 = sorted(l, key=lambda x: x > 0)
l2 = sorted(l, reverse=True)

d = {}

# dont warn since d is a dict and does not have a .sort() method
d = sorted(d)

l = sorted(l, lambda x: x)  # type: ignore
