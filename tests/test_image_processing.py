def test_crop():  
    from image_processing import crop
    import numpy as np
    test_img = (255*np.random.random((100,100))).astype('uint8')
    test_img[11:40,20:40]= 0
    cont =[[21,12],[39,12],[39,39],[21,12]]    
    assert (crop(test_img,np.array(cont))==0).all()    