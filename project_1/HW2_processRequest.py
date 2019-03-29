from __future__ import print_function # Python 2/3 compatibility
import json
import boto3
import time
from botocore.vendored import requests
from collections import Counter


def lambda_handler(event, context):
	message = pullSQS()
	while message:
		print("message=",message)
		suggestion = getSugest(message)
		print("suggestion=",suggestion)
		sendSMS(message, suggestion)
		writeDatabase(message, suggestion)
		message = pullSQS()


def getSugest(message):
	message = eval(message)
	location = message["location"]
	cuisine = message["cuisine"]
	phone = message["phone"]
	date = message["date"]
	people = message["people"]
	time = message["time"]
	
	URL = "https://maps.googleapis.com/maps/api/place/textsearch/json?query="+cuisine+"+restaurant+in+"+location
	r = requests.post(url = URL, data = "whatever")
	data = r.json()
	c = Counter(player['name'] for player in data["results"])
	c = len(c)
	if c>3:
		c = 3
	SMSmessage = "Hello! Here are my "+cuisine+" restaurant suggestions for "+people+" people, for "+date+" at "+time+":"
	for x in range(c):
		SMSmessage+=" "+str(x+1)+". "+data["results"][x]["name"]+", located at "+data["results"][x]["formatted_address"]+", its rating is "+str(data["results"][x]["rating"])	

	return SMSmessage
	
	
def pullSQS():
	sqs = boto3.resource('sqs')
	queue = sqs.get_queue_by_name(QueueName='LexMessage')
	for mes in queue.receive_messages(MaxNumberOfMessages=1):
		if mes:
			message = mes.body
			mes.delete()
			return message
		else:
			return False
	

def sendSMS(message, suggestion):
	sns = boto3.client(
		"sns",
		aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION_NAME
	)
	#print('+1'+str(eval(message)['phone']))
	sns.publish(
		PhoneNumber = '+1'+str(eval(message)['phone']),
		Message = suggestion
	)
	
	
def writeDatabase(message, suggestion):
	dynamodb = boto3.client('dynamodb')  #dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
	table_name = 'record'
	exist = dynamodb.list_tables()['TableNames']
	print('exist=',exist)
	if table_name not in exist:
		response = dynamodb.create_table(
			TableName = table_name,
			KeySchema = [
				{
					'AttributeName': 'phoneNumber',
					'KeyType': 'HASH'  #Partition key
				},
				{
					'AttributeName': 'recordTime',
					'KeyType': 'RANGE'  #sort key
				}
			],
			AttributeDefinitions=[
				{
					'AttributeName': 'phoneNumber',
					'AttributeType': 'S'    #string
				},
				{
					'AttributeName': 'recordTime',
					'AttributeType': 'S'  #string
				}
			],
			ProvisionedThroughput={
				'ReadCapacityUnits': 10,
				'WriteCapacityUnits': 10
			}
		)
		time.sleep(20)
		print(response)
	else:
		print('exist')
	
	phNum = eval(message)['phone']
	recTime = str(time.time())
	response = dynamodb.put_item(
		TableName = table_name,
		Item = {
			'phoneNumber': {
				'S' : phNum
			},
			'recordTime': {
				'S' : recTime
			},
			'suggestion': {
				'S' : suggestion
			},
			'message' : {
				'S' : message
			}
		}
	)
	#print(response)

