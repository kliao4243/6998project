import json
import pymongo
import requests
import re

def lambda_handler(event, context):
    unprocess = event["image"]
    
    # get the type of the image
    if ".jpg" in unprocess:
        TYPE = "jpg"
    elif ".jpeg" in unprocess:
        TYPE = "jpeg"
    elif ".png" in unprocess:
        TYPE = "png"
    ID = event["user"]
    my_re = "(.*)."+TYPE
    
    # get the colorized and styled images
    temp_name = re.findall(my_re, unprocess)[0]
    processed = [temp_name+"_colorized."+TYPE]
    processed.append(temp_name+"_rain_princess."+TYPE)
    processed.append(temp_name+"_la_muse."+TYPE)
    processed.append(temp_name+"_udnie."+TYPE)
    processed.append(temp_name+"_wave."+TYPE)
    processed.append(temp_name+"_scream."+TYPE)
    processed.append(temp_name+"_wreck."+TYPE)
    
    
    # save these records to mongoDB and set status to false, meaning that the images haven't been processed
    client = pymongo.MongoClient("mongodb+srv://kunjian:iotproject@cluster0-ttnra.mongodb.net/test?retryWrites=true")
    mydb = client["Cloud-Computing"]
    photorecord = mydb["photos"]
    if photorecord.find_one({'user':ID}) is None:
        photorecord.insert_one({'user':ID,'unprocess':unprocess, 'processed':processed, 'status':False})
    elif photorecord.find_one({'user':ID, 'unprocess':unprocess}) is None:
        photorecord.insert_one({'user':ID,'unprocess':unprocess, 'processed':processed, 'status':False})
    print(event)
    # send requests to EC2 thus it begins to process images
    r = requests.post('http://34.231.147.104:8080', data = {'user':ID, 'image':unprocess})
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
