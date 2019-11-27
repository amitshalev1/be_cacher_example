import cv2

def draw_annoations(img,annots):
    """
    draw segmentations on image
    img : np.array
    annots: maagad format
    """
    font = cv2.FONT_HERSHEY_PLAIN
    for annot in annots:
        if annot['deleted']!=1:
            if annot['annotation_type']=='polygon':
                img = draw_polygon(img,annot['annotations'])
            elif annot['annotation_type']=='oval':
                print(annot['annotations'])
                box=[(annot['annotations']['x'],annot['annotations']['y']),
                                 (annot['annotations']['x']+annot['annotations']['width'],annot['annotations']['y']),
                                 (annot['annotations']['x'],annot['annotations']['y']+annot['annotations']['height']),
                                 (annot['annotations']['x']+annot['annotations']['width'],annot['annotations']['y']+annot['annotations']['height'])]
                box=[int(x) for x in box]
                cv2.ellipse(img,box, (0,0,0),18)

    fig, ax = plt.subplots(figsize=(10, 22))
    ax.imshow(img, interpolation='nearest')


def draw_polygon(img,ploygon,x='x',y='y'):
    '''
    adds a polygon to the img and returns the new img
    polygon= [{'x':23,'y':531}]
    '''
    contour = np.array([(point[x],point[y]) for point in ploygon,dtype=np.int32)
    cv2.drawContours(img,[contour] ,0, (0,0,0),18)