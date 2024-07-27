import boto3
import urllib.parse
import json
import pandas as pd
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
  
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('StudyDynamoTable') 
    #print(event)
    
    http_method = event['httpMethod']
    
    if http_method == 'GET':
        condition_keys = set()
        ddbResponse = table.scan()
        
        for item in ddbResponse['Items']:
            if item['PK'].startswith('s#'):
                condition_keys.add(item['PK'])
                
        # Handle pagination if necessary
        while 'LastEvaluatedKey' in ddbResponse:
            ddbResponse = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            for item in ddbResponse['Items']:
                if item['PK'].startswith('s#'):
                    condition_keys.add(item['PK']) 
                    
        # Convert the set to a list
        condition_list = list(condition_keys)
        condition_list2=[condition[2:] for condition in condition_list]
        condition_list2.sort()
        response = {
            'statusCode': 200,
            'headers': {
            "Access-Control-Allow-Headers" : "Content-Type, x-api-key",
            "Access-Control-Allow-Origin": "*", # Allow from anywhere 
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS" # Allow only GET request 
            },
            'body': json.dumps(condition_list2)
        }
        
    elif http_method == 'POST':
        # Parse request body
        parsed_body = urllib.parse.parse_qs(event['body'])
        # Convert the parsed query to a simple dictionary
        form_variables = {k: v[0] for k, v in parsed_body.items()}
        signup_condition = form_variables['condition']
        ddbResponse  = table.query(
            KeyConditionExpression = Key('PK').eq('d#DISEASES') & Key('SK').eq('d#'+signup_condition.upper()))
        print(ddbResponse)
        if ddbResponse['Count']>0:
            for Item in ddbResponse['Items']:
                conditions=Item['SK'][2:]
                condition_list=conditions.split(',')
                for condition in condition_list:
                    ddbResponse = table.put_item(
                                    Item={
                                        'PK':'n#'+condition,
                                        'SK':'n#'+form_variables['user_email']
                                    })
        response = {
            'statusCode': 200,
            'headers': {
            "Access-Control-Allow-Headers" : "Content-Type, x-api-key",
            "Access-Control-Allow-Origin": "*", # Allow from anywhere 
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS" # Allow only GET request 
            },
            'body': 'Data Saved.'
        } 
    elif http_method == 'OPTIONS':  
        response = {
            'statusCode': 200,
            'headers': {
            "Access-Control-Allow-Headers" : "Content-Type, x-api-key",
            "Access-Control-Allow-Origin": "*", # Allow from anywhere 
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS" # Allow only GET request 
            }
        }                 
    else:
        # Handle unsupported method
        response = {
            'statusCode': 405,
            'body': json.dumps({
                'message': 'Method Not Allowed'
            })
        }
    
    return response