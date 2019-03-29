import json
import boto3
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import requests


def detect_labels(bucket, key):
	rekognition = boto3.client('rekognition')
	response = rekognition.detect_labels(
		Image={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		MaxLabels=10,
		MinConfidence=90
	)
	return response['Labels']

def uploadES(tags):
	host = '' # The domain with https:// and trailing slash. For example, https://my-test-domain.us-east-1.es.amazonaws.com/
	path = '/photos/_doc' # the Elasticsearch API endpoint
	region = '' # For example, us-west-1

	service = 'es'
	#credentials = boto3.Session().get_credentials()
	awsauth = AWS4Auth('', '', region, service)
	url = host + path
	#r = requests.get(url, auth=awsauth, params=payload)
	r = requests.post(url, auth=awsauth, json=tags) # requests.get, post, and delete have similar syntax
	#r = requests.delete(url, auth=awsauth)
	print(r.text)
	
def testES():
	client = boto3.client('es')
	response = client.add_tags(
		ARN='',
		TagList=[
			{
				'Key': 'string',
				'Value': 'string'
				
			},
			]
		)

def lambda_handler(event, context):
    # TODO implement
	BUCKET = event["Records"][0]["s3"]["bucket"]["name"]
	OBJECT = event["Records"][0]["s3"]["object"]["key"]
	#results = detect_labels("photo-bucket-1", "banff-springs-winter.jpg")
	results = detect_labels(BUCKET, OBJECT)
	labels = list()
	for result in results:
		labels.append(result["Name"])
	tag = dict()
	tag["objectKey"] = OBJECT
	tag["bucket"] = BUCKET
	tag["createdTimestamp"] = str(datetime.now())
	tag["labels"] = labels
	#print(tag)
	uploadES(tag)
	#testES()
	return {
        'statusCode': 200,
        'body': json.dumps(results[0]["Name"])
    }
