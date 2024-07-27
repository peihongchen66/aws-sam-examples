#Before running this Lambda, register and verify sender email following below instruction
#https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html
import json
import boto3
import requests
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    print(event)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('StudyDynamoTable') 
    
    sesClient = boto3.client('ses')
    fromEmail = 'test1@example.com'
    title = 'Clinical Study Enrollment Notification'
    
    if 'Records' in event:
        for record in event['Records']:
            if ((record['eventName']=='INSERT' and 'overallStatus' in record['dynamodb']['NewImage']
                and record['dynamodb']['NewImage']['overallStatus']['S']=='RECRUITING')
                or (record['eventName']=='MODIFY' and 'overallStatus' in record['dynamodb']['NewImage']
                and 'overallStatus' in record['dynamodb']['OldImage']
                and record['dynamodb']['OldImage']['overallStatus']['S']!='RECRUITING'
                and record['dynamodb']['NewImage']['overallStatus']['S']=='RECRUITING')):
                    condition = record['dynamodb']['Keys']['PK']['S'][2:]
                    nctID = record['dynamodb']['Keys']['SK']['S'][2:]
                    ddbResponse = table.query(
                        KeyConditionExpression=Key('PK').eq('n#'+condition) & Key('SK').begins_with('n#')
                    )
                    print(ddbResponse)
                    if ddbResponse['Count']!=0:
                        """
                        studyResponse = requests.get(
                            url='https://clinicaltrials.gov/api/v2/studies?filter.ids='+nctID,
                            headers={'Accept': 'application/json'},
                            timeout=5)
                        emailbody = json.dumps(studyResponse.json()) if studyResponse and studyResponse.status_code == 200 else None
                        """
                        emailbody = f'The below clinical study is enrolling. Click on the link for details.  https://clinicaltrials.gov/api/v2/studies?filter.ids={nctID}'
                        print(emailbody)
                    for item in ddbResponse['Items']:
                        toEmail = item['SK'][2:]
                        sesResponse = sesClient.send_email(
                            Destination={'ToAddresses': [toEmail]},
                            Message={'Body': {
                                    'Text': {
                                        'Charset': 'UTF-8',
                                        'Data': emailbody,
                                    }
                                },
                                'Subject': {
                                    'Charset': 'UTF-8',
                                    'Data': title,
                                },
                            },
                            Source=fromEmail
                        )
                
                
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }