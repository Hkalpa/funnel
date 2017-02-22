def tester():
    test(2,1,3,4,26)
    test(1,1,1,1,3)
    test(10,20,30,40,2410)
    test(4,3,2,1,8)
    test(100,10,98,99,21856)
    test(54,32,51,96,16496)

def test(a, b, l, N, result):
    if func(a, b, l, N) == result:
        print("OK    \t", [a, b, l, N], "\t", result, "\t", func(a, b, l, N))
    else:
        print("FAILED\t", [a, b, l, N], "\t", result, "\t", func(a, b, l, N))

def func(a, b, l, N):
    result = 0
    
    return a + 2*l + (N-1)*(2*a + 2*b)


tester()