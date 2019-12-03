from keras.applications.mobilenet import preprocess_input
from keras.preprocessing.image import img_to_array, load_img
from image_processing import crop,get_contour,crop_generator
import cv2
import pandas as pd
import numpy as np

def get_resnet50():
    from keras.applications.resnet50 import ResNet50
    from keras import backend as K
    K.clear_session()
    nn = ResNet50(include_top=False, weights='imagenet', input_shape=(224,224,3), pooling='avg')
    nn.compile('sgd','categorical_crossentropy')
    return nn  

def img_as_arr(path:str,target_size=(224,224)): 
    '''
    input an image paths
    output np array scaled -1 to 1
    '''
    return img_to_array(load_img(path, target_size=target_size))
    
def load_images(imgs:list):
    '''
    get a list of np array output a generator fit for resnet model
    '''

    return (np.expand_dims(preprocess_input(im), axis=0) for im in imgs) 

def image_generator(imgs:list,target_size=(224,224)):
    '''
    input a list of paths
    output generator for model prediction
    '''
    return load_images((img_as_arr(x) for x in imgs))


def get_resnet_activation_for_paths(paths:list,
                                    paths_column = 'paths' ,
                                    activations_column = 'act'):
    '''
    input list of paths
    outout : dataframe with paths column and activations column
    '''
    return pd.DataFrame({paths_column:paths,
                activations_column:get_resnet50().predict_generator(image_generator(paths),steps=len(paths)).tolist()})    
    

def get_resnet_activation_for_crop(df,
                                   target_size = (224,224),
                                   paths_column = 'paths' ,
                                   activations_column = 'act',
                                   thresh = 5):

    '''
    input - > df: dataframe containing image_uri and annotations columns
    output df paths, activations
    '''
    filtered_cropped,filtered_paths = crop_generator(df[['image_uri','annotations']].values)
    return pd.DataFrame({paths_column:filtered_paths,
                activations_column:get_resnet50().predict_generator(load_images(filtered_cropped),steps=len(filtered_paths)).tolist()})



