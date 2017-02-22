def func(classes):
    result = 0
    for pupils in classes:
        result += (pupils // 2) + (pupils % 2)
    
    return result

def test(list, result):
    if func(list) == result:
        print("OK    ", list, "\t", result, "\t", func(list))
    else:
        print("FAILED", list, "\t", result, "\t", func(list))

def tester():
    test([20, 21, 22], 32)
    test([26, 20, 16], 31)
    test([25, 21, 23], 36)
    test([17, 19, 18], 28)


tester()