import boto3
import json
import datetime
import time
import os
import logging
import elasticsearch
from requests_aws4auth import AWS4Auth
import requests

"""
def lambda_handler(event, context):
    query = str(event['queryStringParameters']['q'])     #get user's query
    
    #your json response
    respBody = json.dumps({      
        "query" : query
    })
    
    response = {
        "isBase64Encoded": False,
        "statusCode" : 200,
        "headers" : { 
            #your response header 
        },
        "body" : respBody
    }
    return response



"""

def searchES(tags):
    host = ''  # The domain with https:// and trailing slash. For example, https://my-test-domain.us-east-1.es.amazonaws.com/
    region = 'us-east-1'  # For example, us-west-1
    index = "photos"

    service = 'es'
    # credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth('', '', region, service)
    url = host + '/' + index + '/_search'
    headers = {"Content-Type": "application/json"}

    if tags[1]:
        query = {"query": {"bool": {"must": [{"match": {"labels": tags[0]}}, {"match": {"labels": tags[1]}}]}}}

    else:
        query = {"query": {"match": {"labels": tags[0]}}}

    r = requests.get(url, auth=awsauth, headers = headers, data=json.dumps(query)) # requests.get, post, and delete have similar syntax
    # print(r.text)
    # print(tags)
    return r
    
def lambda_handler(event, context):
    inputText = str(event['queryStringParameters']['q'])     #get user's inputText
    client = boto3.client('lex-runtime')
    lex_response = client.post_text(botName = 'photo_search_query', botAlias = '$LATEST', userId='bot_demo', inputText = inputText)
    message = lex_response['message']
    response = {
        "isBase64Encoded": False,
        "statusCode" : 200,
        "headers" : { 
        #your response header 
        },
    }
    response['message'] = message
    try:
        tagA = lex_response['slots']['tagA']
        tagB = lex_response['slots']['tagB']
        # print([tagA, tagB])
        r = searchES([tagA, tagB])
        response['body'] = r.text
        # if tagB:
        #     print("ojbk")
        
    except:
        return response
    
    return response
