import json
import pymongo
import requests

def lambda_handler(event, context):
    ID = event["user"]
    client = pymongo.MongoClient("mongodb+srv://kunjian:iotproject@cluster0-ttnra.mongodb.net/test?retryWrites=true")
    mydb = client["Cloud-Computing"]
    photorecord = mydb["photos"]
    
    # prepare the url of the bucket
    url = 'https://s3.amazonaws.com/6998project/'
    url_list = dict()
    url_list['unprocess'] = []
    url_list['processed'] = []
    url_list['processing'] = 0
    
    # get url of the unprocessed image
    for img in photorecord.find({'user':ID, 'status':True}):
        url_list['unprocess'].append(img['unprocess'])
    for i in range(len(url_list['unprocess'])):
        url_list['unprocess'][i] = url + url_list['unprocess'][i]
        
    # get urls of processed images
    for img_list in photorecord.find({'user':ID, 'status':True}):
        for img in img_list['processed']:
            url_list['processed'].append(img)
            
    for img_list in photorecord.find({'user':ID, 'status':False}):
        url_list['processing']+=1
            
    for i in range(len(url_list['processed'])):
        url_list['processed'][i] = url + url_list['processed'][i]

    # TODO implement
    return {
        "statusCode": 200,
        "headers" : { 
            "Access-Control-Allow-Origin":"*"
        },
        "body": json.dumps(url_list)
    }
