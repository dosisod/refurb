x = " "

# these should match

f"{x}"
f"{123}"


# these should not

f"hello{x}world"
f"{x} {x}"

f"{x:{x}}"
