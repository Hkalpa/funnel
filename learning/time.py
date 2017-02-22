def func(n):
    a = (n // 60) % 24
    b = n % 60
    return [a, b]

def test(inp, a, b):
    if func(inp) == [a, b]:
        print("OK    ", inp, "\t", [a, b], "\t", func(inp))
    else:
        print("FAILED", inp, "\t", [a, b], "\t", func(inp))

def tester():
    test(150,2,30)
    test(1441,0,1)
    test(444,7,24)
    test(180,3,0)
    test(1439,23,59)
    test(1440,0,0)
    test(2000,9,20)
    test(3456,9,36)
    test(5678,22,38)
    test(9876,20,36)

tester()
