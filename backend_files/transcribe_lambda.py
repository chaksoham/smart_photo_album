import json
import boto3
import time
import urllib

client = boto3.client('transcribe')


def lambda_handler(event, context):
    # TODO implement
    def extract_info(event):
        put_info = event.get('Records')[-1]
        bucket_key = put_info.get('s3').get('bucket').get('name')
        audio_key = put_info.get('s3').get('object').get('key')
        time_key =  put_info.get('eventTime')
        return bucket_key, audio_key, time_key
    
    def extract_text(response):
        task_name = response.get("TranscriptionJob").get("TranscriptionJobName")
        task_url = response.get("TranscriptionJob").get("Transcript").get("TranscriptFileUri")
        script_json = urllib.request.urlopen(task_url).read();
        script_json = json.loads(script_json)
        ans = script_json.get("results").get("transcripts")[0].get("transcript")
        return ans
    
    bucket_key, audio_key, time_key = extract_info(event)
    test_audio_path = "https://s3.amazonaws.com/{0}/{1}".format(bucket_key, audio_key)
    test_name = 'test'
    
    try :
        client.delete_transcription_job(
        TranscriptionJobName=test_name
        )  # delete the job from console
    except:
        pass
    
    stt_response = client.start_transcription_job(
    TranscriptionJobName=test_name,
    OutputBucketName='cc-b2',
    LanguageCode='en-US',
    MediaFormat='mp3',
    Media={
        'MediaFileUri': test_audio_path
    })
    
    time.sleep(3)
    
    while stt_response["TranscriptionJob"]["TranscriptionJobStatus"] == "IN_PROGRESS":
        stt_response = client.get_transcription_job(
            TranscriptionJobName=test_name
            )
        time.sleep(1) # 'save load'
    
    sentence = ""
    
    if stt_response["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
        sentence = extract_text(stt_response)
    
    print(sentence)
        
    return {
        'statusCode': 200,
        'body': sentence # return the stt result
    }