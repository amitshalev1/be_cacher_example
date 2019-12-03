import os
import pickle
import time 
from multiprocessing import Pool
import threading
from tqdm import tqdm_notebook as tqdm
import h5py
import numpy as np
import cv2
import hashlib
import pandas as pd

IMG_FOLDER='thumbs/'

IMAGES_ENDINGS = ['jpg', 'png', 'iff', 'tif', 'gif']

def load_images(imgs):
    from keras.applications.mobilenet import preprocess_input
    from keras.preprocessing.image import img_to_array, load_img
    def img_as_arr(path): 
        return preprocess_input(img_to_array(load_img(path, target_size=(224,224))))


    arr = np.array([img_as_arr(im) for im in tqdm(imgs, leave=False)])
    return arr 


def get_resnet50():
    from keras.applications.resnet50 import ResNet50
    from keras import backend as K
    K.clear_session()
    nn = ResNet50(include_top=False, weights='imagenet', input_shape=(224,224,3), pooling='avg')
    nn.compile('sgd','categorical_crossentropy')
    return nn  

def pass_batch_trough_resnet50(imgs):
    import tensorflow as tf
    from keras import backend as K
    K.clear_session()
    tf.reset_default_graph()
    arr = load_images(imgs)
    nn = get_resnet50()
    return nn.predict(arr, verbose=1, batch_size=64)
  

def create_thumbnail(fn,im_id, target_dir='thumbs/', resize=224):
    flags = cv2.IMREAD_UNCHANGED+cv2.IMREAD_ANYDEPTH+cv2.IMREAD_ANYCOLOR
    target_f = target_dir+str(im_id)+'.jpg'
    im = cv2.resize(cv2.imread(fn, flags),  (resize, resize))
    cv2.imwrite(target_f, im)
    



import multiprocessing

def create_thumbs(df,image_folder=IMG_FOLDER):

    df=df[~df['image_uri'].str.contains('.txt')]
    def worker(val):
        create_thumbnail(val[1],val[0],target_dir=image_folder)
    jobs=[]
    for val in tqdm(df[['image_id','image_uri']].values):
        p = multiprocessing.Process(target=worker, args=(val,))
        #p = multiprocessing.Process(target=worker)
        jobs.append(p)
        p.start()
    #         jobs[-1].terminate()

    for j in jobs:
        j.join()            
            
def precompute_activations_resnet50(df,new_fol,batch_size=256*4):
    #require reqrite to the hdf5 version!
    imgs=(new_fol+df['image_id'].astype(str)+'.jpg').values.tolist()
    ACTIVE_HDF5='temp_act.h5'
    batches = range(0,len(imgs),batch_size)
    batches = [imgs[batch:batch+batch_size] for batch in batches]
    sorage_shape = (len(imgs), 2048)
    with h5py.File(ACTIVE_HDF5, 'w') as f:
        f.create_dataset('resnet50', sorage_shape, np.float32, chunks=(128, 2048), maxshape=(None, 2048))
        for idx, batch in enumerate(tqdm(batches, leave=False)):
            activations = pass_batch_trough_resnet50(batch) #this is cached...
            pos_start, pos_end = idx*batch_size, idx*batch_size + activations.shape[0]
            f['resnet50'][pos_start : pos_end] = activations   
    filename = "temp_act.h5"
    f = h5py.File(filename, 'r')

    # List all groups
    print("Keys: %s" % f.keys())
    a_group_key = list(f.keys())[0]

    # Get the data
    data = list(f[a_group_key])
    f.close()  
    df['act']=data
    
#get dataframe,return with activations
def get_activations(df):
    assert 'image_id' in df.columns,'must provide dataframe with image_id column'
    assert 'image_uri' in df.columns,'must provide dataframe with image_uri column'  
    df['image_id']=df['image_id'].astype(int)
    new_fol='new_folder_just_for_thumbs/'
    if new_fol in os.listdir():
        shutil.rmtree(new_fol)
    try:
        os.mkdir(new_fol)
    except:
        shutil.rmtree(new_fol)
        os.mkdir(new_fol)
    create_thumbs(df,image_folder=new_fol)
    precompute_activations_resnet50(df,new_fol)
    shutil.rmtree(new_fol)
    return df
  


def poc_data_download(ex_id,redo=False):
    if not os.path.isfile('data_for_ex'+str(ex_id)+'.parquet') or redo:   
        dummy.renew_auth()
        #get imaging task for experiment
        imageing_tasks=list(filter(lambda x:x['experiment_id']==ex_id,dummy.api_get('get_imaging_tasks')))
        #download images by imaging tasks
        imgs=[]
        for i,image_task in enumerate(imageing_tasks):
            for x in dummy.api_get('get_images_by_task_id',task_id=image_task['task_id']):
                x['time']=i
                imgs.append(x)    
        dummy.renew_auth()        
        #download experiment map
        exmap=dummy.api_get('get_experiment_map',experiment_id=ex_id)
        exmap=pd.DataFrame(exmap['experiment_map_list'])

        #download by plot
        frames=[]
        for plot in tqdm(exmap['Plot'].unique()):
            df=pd.DataFrame(dummy.api_get('get_images_by_plot_name',experiment_id=ex_id,plot_name=plot))
            df['Plot']=plot
            frames.append(df)
        dummy.renew_auth()
        #merge ,get activations and save
        temp=pd.concat(frames)
        expimgs=pd.merge(temp,exmap,on='Plot')
        expimgs['image_id']=expimgs['image_id'].astype(int)
        expimgs=pd.merge(expimgs,pd.DataFrame(imgs),on=['image_id','frame_id','image_uri'])
        reslist=[]
        for f in tqdm(expimgs['frame_id'].unique()):
            reslist+=dummy.try_(dummy.api_get,api_func='get_images_by_frame',frame_id=f,detail_level='detailed')
            #reslist+=dummy.api_get('get_images_by_frame',frame_id=f,detail_level='detailed')
        dummy.renew_auth()
        expimgs=pd.merge(expimgs,pd.DataFrame(reslist),on=['image_id','frame_id','image_uri']) 
        expimgs.to_parquet('data_for_ex'+str(ex_id)+'.parquet')        
        get_activations(expimgs)
        expimgs.to_parquet('data_for_ex'+str(ex_id)+'.parquet')
    else:
        expimgs=pd.read_parquet('data_for_ex'+str(ex_id)+'.parquet')
    return expimgs