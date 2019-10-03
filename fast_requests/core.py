import requests

def api_post(base_url,api_func,auth="",**kwargs):
    url =  base_url+api_func+'/'
    headers={ "Content-Type" : "application/json", "Accept" : "application/json"} 
    if auth!="":    headers['Authorization'] = 'JWT '+auth
    params={}
    for key, value in kwargs.items():
        params[key]=value
    r = requests.post(url, headers=headers, json=params)             
    return r 


def api_get(base_url,api_func,auth="",**kwargs):
    url =  base_url+api_func+'/'
    empty='?'
    for key, value in kwargs.items():
        empty+= str(key)+'='+ str(value) +'&'
    empty=empty[:-1]
    url=url+empty
    params = {'Accept': 'application/json'}
    if auth!="":    params['Authorization'] = 'JWT '+auth
    r = requests.get(url,  headers=params) 
    return  r