def test_crop():  
    from image_processing import crop
    import numpy as np
    test_img = (255*np.random.random((100,100))).astype('uint8')
    test_img[11:40,20:40]= 0
    cont =[[21,12],[39,12],[39,39],[21,12]]    
    assert (crop(test_img,np.array(cont))==0).all()    


def test_draw_polygon():
    from image_processing import draw_polygon
    import numpy as np
    import cv2
    img = 255*np.ones((100,100,3)) # original empty rgb image
    polygon = [{'x':25,'y':75},
               {'x':75,'y':75},
               {'x':50,'y':25}]   # triangle

    assert np.array_equal(draw_polygon(img,polygon,thickness=3),cv2.imread('test_draw_polygon_image.png'))


    assert np.array_equal(img , 255*np.ones((100,100,3)))
        