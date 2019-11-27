from .phenomics_api import *
from tqdm import tqdm_notebook as tqdm
import cv2
import ntpath


dummy=Phenomics()

dummy.login('amits','4rfv4rfv')



#download get_annotations

def PolyArea(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def get_image_uri(image_id):
    return dummy.try_(func=dummy.api_get,api_func='get_image_data',image_id=image_id)['image_uri']

def get_images_multi(df):
    from multiprocessing import Pool
    p=Pool(40)
    return filter(None.__ne__,p.map(get_image, tqdm(df.image_id.sort_values().unique())))

def get_image(idx):
    try:
        uri=get_image_uri(idx)
        file_name=ntpath.basename(uri.replace('/mnt/gluster/catalog/',TARGET_DIR))
        img=cv2.imread(uri)
        height=img.shape[0]
        width=img.shape[1]

        return {
            'file_name' : file_name,
            'coco_url':uri.replace('/mnt/gluster/catalog/',TARGET_DIR),
            'path' : uri.replace('/mnt/gluster/catalog/',TARGET_DIR),
            'height' :height,
            'width' : width,
            'id' : idx
        }
    except:
        print(idx)
    
    


def get_images(df):
    print('getting images')
    res = []
    for idx in tqdm(df.image_id.sort_values().unique()):
        try:
            uri=get_image_uri(idx)
            file_name=ntpath.basename(uri.replace('https://annotator.agri-net.org.il/T/','/mnt/gluster/catalog/'))
            img=cv2.imread(uri)
            
            height=img.shape[0]
            width=img.shape[1]

            res.append({
                'file_name' : file_name,
                'coco_url':uri.replace('https://annotator.agri-net.org.il/T/','/mnt/gluster/catalog/'),
                'path' : uri.replace('https://annotator.agri-net.org.il/T/','/mnt/gluster/catalog/'),
                'height' :height,
                'width' : width,
                'id' : idx
            })
        except:
            print(idx)
    return res
    
def get_categories():
    dummy.renew_auth()
    dummy.api_get('get_dictionary_data',dictionary_name='annotation_objects')
    dicts=dummy.api_get('get_dictionaries')
    categ=[]
    res=[]
    for dic in tqdm(dicts[:-3]):
        if dic['dictionary_name'] not in ['cameras','experiment_purpose','growth_stage','image_type','method','scale']:
            categ=dummy.api_get('get_dictionary_data',dictionary_name=dic['dictionary_name'])[dic['dictionary_name']]   
            name=list(filter(lambda x: x.endswith('_name'),np.random.choice(categ).keys()))[0]
            for item in categ:
                res.append({
                    'id':item['record_id'],
                    'name':item[name],
                    'supercategory':dic['dictionary_name'],
                    "isthing" : 1,
                    "color" : [255,255,255],            
                })
    return res    
    
def get_categories_simple():
    res=[]
    res.append({
        'id':0,
        'name':"backgroung",
        'supercategory':"things",
        "isthing" : 0,
        "color" : [255,255,255],            
    })
    res.append({
        'id':1,
        'name':"object",
        'supercategory':"things",
        "isthing" : 1,
        "color" : [255,255,255],            
    })    
    return res   



def get_annotations(df,images,rec_id=1967):
    print('getting annotations')
    res = []
    
    for idx,item in tqdm(enumerate(df[df.image_id.isin(list(map(lambda x: x['id'],images)))].to_dict(orient='records'))):
        if item['annotation_type']!='tag' and item['deleted']==0:
            annot=item['annotations']
            if type(annot)!=list:
                annot=[annot]
            annot_df=pd.DataFrame(annot)
            x,y=annot_df.x.astype(int),annot_df.y.astype(int)
            im_id=1
            try:
                im=list(filter(lambda x:x['id']==item['image_id'],images))[0]    
            except:
                print(item['image_id'],images)
            h=im['height']
            w=im['width']
#             if  "'record_id': "+str(rec_id) in str(item['annotation_dictionary_records']):
#                 c=rec_id
#             else:
#                 c=1
            c=1
            if len(x) > 2:
                x[x<0] = 0 #fix negative values
                y[y<0] = 0 #fix negative values
                x[x>w] = w #fix negative values
                y[y>h] = h #fix negative values
                res.append({
                    "id": idx,
                    "segmentation": [ [int(c) for coord in list(zip(x,y)) for c in coord] ],
                    "image_id" : item['image_id'],
                    "area" : PolyArea(x, y),
                    "category_id" : c,
                    "bbox" : [min(x), min(y), max(x) - min(x), max(y) - min(y)],
                    'iscrowd' : 0
                })
    return res




def get_info():
    return {
        'description' : " ",
        'date_created' : "",
        'version' : 1.0,
        'contributur' : 'PHENOMICS HAZERA ISRAEL'
    }


def agrinet_annotations_to_coco(res):
    res=sum([list(x) for x in res.values()],[])
    df=pd.DataFrame(res)
    res=[]

    images=get_images(df)
    res = {
        'categories' : get_categories_simple(),
        'images' : images,
        'annotations' : get_annotations(df,images),
        'info' : get_info()
    }

    return res

def save_coco_to_json(coco,save_to):
    def default(o):
        if isinstance(o, np.int64): return int(o)  
        raise TypeError

    with open(save_to, 'w') as f:
        json.dump(coco, f, ensure_ascii=False, allow_nan=False, default=default)    

def get_coco(annotation_task_id):
    # annotation_task_id=10
    res = dummy.try_(dummy.api_get,api_func='get_annotations',annotation_task_id=annotation_task_id)
    res=sum([list(x) for x in res.values()],[])
    df=pd.DataFrame(res)
    res=[]

    images=get_images(df)
    res = {
        'categories' : get_categories(),
        'images' : images,
        'annotations' : get_annotations(df,images),
        'info' : get_info()
    }

    def default(o):
        if isinstance(o, np.int64): return int(o)  
        raise TypeError

    with open('segmentation_results'+str(annotation_task_id)+'.json', 'w') as f:
        json.dump(res, f, ensure_ascii=False, allow_nan=False, default=default)    
    
    return 'segmentation_results'+str(annotation_task_id)+'.json'
        
    
def get_cats():
    return [{'id':0,
             'name':'background',
             'supercategory':'cats',
             "isthing" : 1,
             "color" : [0,255,255],            
                },
            {'id':1,
             'name':'thing',
             'supercategory':'cats',
             "isthing" : 1,
             "color" : [255,0,255],            
                }]
    
    
