import json
import boto3
from botocore.vendored import requests
import time

#s3 = boto3.resource("s3")

def detect_labels(photo, bucket):
    print("inside detect_labels")
    client=boto3.client('rekognition')
    print("sending request to rekognition")
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=10)
    print("after rekognition")
    timestamp =time.time()
    print('Detected labels for ' + photo) 
    print()  
    labels = []
    for label in response['Labels']:
        labels.append(label['Name'])
        print ("Label: " + label['Name'])
        print ("Confidence: " + str(label['Confidence']))
        
        
    format = {'objectKey':photo,'bucket':bucket,'createdTimestamp':timestamp,'labels':labels}
    print("sending post request to Elastic search")
    url = "https://vpc-photos-7wskxizvxa7dd463rqaf4zppj4.us-east-1.es.amazonaws.com/photos/0"
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, data=json.dumps(format).encode("utf-8"), headers=headers)
    print("Post request sent")
    return len(response['Labels'])


def lambda_handler(event, context):
    # TODO implement
    print("inside index-lambda!!")
    s3_info = event['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name']
    key_name = s3_info['object']['key']
    
    
    result = detect_labels(key_name, 'photobuket')
    
 
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
    
   