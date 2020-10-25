import json
import os
import math
import dateutil.parser
import datetime
import time
import logging
import boto3
from botocore.vendored import requests


def lambda_handler(event, context):
    # TODO implement
    print("hello from here")
    print(event)
    #event['queryStringParameters']['q']
    text = event['queryStringParameters']['q']
    print(text)
    # userId = event['messages'][0]['unstructured']['id']
    client = boto3.client('lex-runtime')
    response = client.post_text(
        botName='PhotoBot',
        botAlias='PhotoChatbot',
        userId='1111',
        inputText=text
        # version='$LATEST'
    )
    
    print('**response**')
    print(response)
    '''
    responseText = response['slots']
    print(responseText)
   
    responseMessages = dict()
    responseMessages["messages"] = [{
        'type': 'string',
        'unstructured': {
            'id': 'string',
            'text': responseText,
            'timestamp': 'string'}}]
    '''
    try:
        if response['slots'] != None:
            response_slots = response['slots'] 
    except:
        response2 = {
            'statusCode': 200,
            'headers':{
                'Access-Control-Allow-Origin':'*',
                'Access-Control-Allow-Credentials':True
            },
            'body': json.dumps(response['message'])
        }

        return response2
    
    # auth = AWS4Auth(os.environ['access_key'], os.environ['secret_key'], 'us-east-1', 'es')
    
    print(response_slots)
    
    
    url = 'https://vpc-photos-7wskxizvxa7dd463rqaf4zppj4.us-east-1.es.amazonaws.com/photos/_search?q='
    
    labels=[]
    if response_slots['Slot'] != None:
        labels.append(response_slots['Slot'])
    if response_slots['Tags'] != None:
        labels.append(response_slots['Tags'])
    
    print("Labels:",labels)
    #labels = ['bird','coat','tree', 'clown']
    resp = []
    for label in labels:
        if (label is not None) and label != '':
            url2 = url+label
            resp.append(requests.get(url2).json())
    print (resp)
    
    output = []
    for r in resp:
        if 'hits' in r:
             for val in r['hits']['hits']:
                key = val['_source']['objectKey']
                if key not in output:
                    output.append(key)
    #url = "https://vpc-photos-b4al4b3cnk5jcfbvlrgxxu3vhu.us-east-1.es.amazonaws.com/photos/_search?pretty=true&q=*:*"
    #print(url)
    #resp = requests.get(url,headers={"Content-Type": "application/json"}).json()
    #resp = requests.get(url)
    
    
    print(output)
    bucket = 'photobuket'
    img_array = []
    for i in output:
        img_url= "https://" + bucket + ".s3.amazonaws.com/" + i
        img_array.append(img_url)
        
    if output != None:
        response = {
            'statusCode': 200,
            'headers':{
                'Access-Control-Allow-Origin':'*',
                'Access-Control-Allow-Credentials':True
            },
            'body': {
                "results":img_array
                
            }
        }
    else:
        response = {
            'statusCode': 200,
            'headers':{
                'Access-Control-Allow-Origin':'*',
                'Access-Control-Allow-Credentials':True
            },
            'body': []
        }
    #logger.debug('event.bot.name={}'.format(event['bot']['name']))
    print(response)
    return response
    