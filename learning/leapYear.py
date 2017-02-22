def func(year):
    if (not year % 4 and year % 100) or not year % 400:
        return "YES"
    return "NO"

def test(value, result):
    var = func(value)
    if var == result:
        print("OK    ", value, "\t", result, "\t", var)
    else:
        print("FAILED", value, "\t", result, "\t", var)

def tester():
    test(2012,"YES")
    test(2011,"NO")
    test(1492,"YES")
    test(1861,"NO")
    test(1600,"YES")
    test(1700,"NO")
    test(1800,"NO")
    test(1900,"NO")
    test(2000,"YES")

tester()
