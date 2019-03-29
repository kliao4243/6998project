import boto3
import json
import datetime
import time
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def recommendation(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    data = {}
    data['location'] = get_slots(intent_request)["Location"]
    data['cuisine'] = get_slots(intent_request)["Cuisine"]
    data['people'] = get_slots(intent_request)["Number_of_people"]
    data['date'] = get_slots(intent_request)["Dining_date"]
    data['time'] = get_slots(intent_request)["Dining_time"]
    data['phone'] = get_slots(intent_request)["Phone_number"]
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='LexMessage')

    queue.send_message(MessageBody=json.dumps(data))
    
    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': "Thank you for your information. Your recommendation will be ready soon. I will send recommendations to your phone in a minute."})


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return recommendation(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')



def lambda_handler(event, context):
    
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    
    return dispatch(event)