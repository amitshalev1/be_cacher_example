def test_1():  
    from breedingeyecacheservice import myfunc
    import os
    assert not os.path.isfile('test_stam.csv')
    print("testing...")
    myfunc() 
    assert os.path.isfile('test_stam.csv')
    os.remove('test_stam.csv')



def test_cmd():
    import os
    assert not os.path.isfile('test_stam.csv')
    print("testing...")
    os.system('python -m breedingeyecacheservice.create_thumbnails')
    assert os.path.isfile('test_stam.csv')
    os.remove('test_stam.csv')
