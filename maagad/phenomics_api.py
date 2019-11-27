import pandas as pd
import requests
import numpy as np
import json
import getpass
import concurrent.futures


'''
use:
p=Phenomics()
df1=p.get_dictioneries()

#long time
dftemp=sum([p.get_dictionary(x)[x].values.tolist() for x in df1.dictionary_name.values.tolist()],[])
temp=[]
for rec in dftemp:
    for typ in set(rec.keys()).difference(set(['record_id','parent'])):
        temp.append({'record_id':rec['record_id'],'field':typ,'value':rec[typ]})
pd.DataFrame(temp)
'''
    
import base64

def encode_base64(mystr):   
    return base64.encodebytes(bytes(mystr, 'utf-8'))

def decode_(mystr):
    return base64.decodebytes(mystr).decode("utf-8") 

def auth(username,password):
    
    url = 'https://www.agri-net.org.il/api/auth/'

    headers = {    "Content-Type": "application/json", "Accept": "application/json"}
    data = json.dumps({"username":username,  "password":password})

    r=requests.post(url, headers=headers, data=data,timeout=5)
    if r.status_code!=200:
        return 'wrong password'
    try:
        res=json.loads(r.text)['access_token']
    except:
        res='wrong password'
    return res



class Phenomics(object):
    
    def verify_auth(self):

        url = 'https://www.agri-net.org.il/api/auth/verify'

        params = {'Authorization':'JWT '+self.auth,'Accept': 'application/json'}
        r = requests.get(url,  headers=params) 
        return json.loads((r.text))['oppstatus']
    
    def __init__(self,is_dev_environemnt=False):
        self.is_dev_environemnt=is_dev_environemnt
        pass
    

    def login(self,username,password):     
        self.auth=auth(username,password)
        self.username=username
        self.password=password
        self.logined=self.verify_auth()=='Ok'
        self.tried_once_already=False
        print('authentication success: ',self.verify_auth())

    def renew_auth(self):
        try:
            self.auth=auth(self.username,self.password)
            return True
        except:
            print('user login problem!')
            return False
     
    
    
    def try_(self,func,**kwargs):
        try:
            res= func(**kwargs)
            if type(res)==dict:
                con= 'message' in res.keys()
            else:
                con= 'message' in str(res)
            if con:
                self.renew_auth()
                return func( **kwargs)  
            else:
                return res

        except:
            self.renew_auth()
            return func( **kwargs)


    def api_post(self,api_func,**kwargs):
        url =  'https://www.agri-net.org.il/api/'+api_func+'/'
        headers={ "Content-Type" : "application/json", "Accept" : "application/json",'Authorization':'JWT '+self.auth} 
        params = {'Authorization':'JWT '+self.auth,'Accept': 'application/json'}
        params={}
        for key, value in kwargs.items():
            params[key]=value
        r = requests.post(url, headers=headers, json=params)             
        return r 


    def api_get(self,api_func,**kwargs):
        url =  'https://www.agri-net.org.il/api/'+api_func+'/'
        empty='?'
        for key, value in kwargs.items():
            empty+= str(key)+'='+ str(value) +'&'
        empty=empty[:-1]
        url=url+empty
        params = {'Authorization':'JWT '+self.auth,'Accept': 'application/json'}
        r = requests.get(url,  headers=params) 
        return  json.loads(r.text)  