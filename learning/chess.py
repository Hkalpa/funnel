def func(one, two):
    if (one[0] % 2 == one[1] % 2) == (two[0] % 2 == two[1] % 2):
        return "YES"
    return "NO"

def test(one, two, result):
    var = func(one, two)
    if var == result:
        print("OK    ", one, two, "\t", result, "\t", var)
    else:
        print("FAILED", one, two, "\t", result, "\t", var)

def tester():
    test([1,1],[2,6],"YES")
    test([2,2],[2,5],"NO")
    test([2,2],[2,4],"YES")
    test([2,3],[3,2],"YES")
    test([2,3],[7,8],"YES")
    test([2,3],[8,8],"NO")
    test([5,7],[5,7],"YES")
    test([2,6],[3,1],"YES")
    test([2,3],[4,5],"YES")
    test([7,2],[2,3],"YES")
    test([1,6],[7,2],"YES")

tester()
