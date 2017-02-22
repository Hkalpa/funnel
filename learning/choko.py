def tester():
    test(4,2,6,"YES")
    test(2,10,7,"NO")
    test(5,7,1,"NO")
    test(7,4,21,"YES")
    test(5,12,100,"NO")
    test(6,6,6,"YES")
    test(6,6,35,"NO")
    test(6,6,37,"NO")
    test(7,1,99,"NO")
    test(300,100,3000,"YES")
    test(256,124,4069,"NO")
    test(348,41,6183,"NO")
    test(387,13,2709,"YES")
    test(13,387,2709,"YES")
    test(1,1,2,"NO")

def test(a, b, N, result):
    var = func(a, b, N)
    if func(a, b, N) == result:
        print("OK    \t", [a, b, N], "\t", result, "\t", var)
    else:
        print("FAILED\t", [a, b, N], "\t", result, "\t", var)

def func(a, b, N):
    if (N % a == 0 or N % b == 0) and a * b > N :
            return "YES"
    return "NO"


tester()