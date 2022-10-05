# these will match

try:
    print()
except:
    pass

try:
    print()
    print()
except Exception:
    pass

try:
    print()
except Exception as e:
    pass

try:
    print()
except (ValueError, FileNotFoundError):
    pass

try:
    print()
except (ValueError, FileNotFoundError) as e:
    pass


# these will not

try:
    print()

except Exception:
    print()

try:
    print()

except:
    pass

finally:
    print("cleanup")

try:
    print()

except:
    pass

else:
    print("no exception thrown")

try:
    print()

except ("not", "an", "exception"):
    pass

try:
    print()

except "not an exception":
    pass
