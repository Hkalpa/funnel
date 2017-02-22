def func(mas):
    return min(mas)

def test(list, result):
    
    var = func(list)
    
    if func(list) == result:
        print("OK    \t", list, "\t", result, "\t", var)
    else:
        print("FAILED\t", list, "\t", result, "\t", var)

def tester():
    test([5,3,7],3)
    test([10,30,4],4)
    test([-5,-3,-3],-5)
    test([1,10,20],1)
    test([74,32,11],11)
    test([50,80,25],25)
    test([3,3,5],3)

tester()