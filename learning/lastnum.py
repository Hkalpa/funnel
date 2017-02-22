def tester():
    test(179,9)
    test(40,0)
    test(101,1)
    test(222,2)
    test(1923,3)
    test(74,4)
    test(505,5)
    test(996,6)
    test(3487,7)
    test(308,8)
    test(1,1)
    test(2,2)
    test(3,3)
    test(4,4)
    test(5,5)
    test(6,6)
    test(7,7)
    test(9,9)
    test(10,0)

def test(a, result):
    var = func(a)
    if func(a) == result:
        print("OK    \t", a, "\t", result, "\t", var)
    else:
        print("FAILED\t", a, "\t", result, "\t", var)

def func(a):
    return a % 10


tester()