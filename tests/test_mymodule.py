def test_1():  
    from mymodule import myfunc
    print("testing...")
    assert myfunc() 

def test_that_fails():
    assert False