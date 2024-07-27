import requests
import boto3
from boto3.dynamodb.conditions import Key, Attr
import pandas as pd
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('StudyDynamoTable')
    
    ddbResponse  = table.query(
            KeyConditionExpression = Key('PK').eq('CANCER'))
                        
    if ddbResponse['Count']==0:  
        diseaseDF=pd.read_csv('disease_mapping.csv', sep='|')
        with table.batch_writer() as batch:
            for index, row in diseaseDF.iterrows():
                item = {
                    'PK' : 'd#DISEASES',
                    'SK' : 'd#'+row['SIGNUP_DISEASE'].upper(),
                    'KeyWords' : 'd#'+row['STUDY_DISEASE_CONDITION'].upper()
                }
                batch.put_item(Item=item)
                
   
    ddbResponse = table.query(
                        KeyConditionExpression=Key('PK').eq('d#DISEASES')&Key('SK').begins_with('d#')
                    )        
            
    conMap={}
    for item in ddbResponse['Items']:
        for keyWord in item['KeyWord'][2:].split(','):
            conMap.update({keyWord:item['SK'][2:]})
    conMapKeyList=list((conMap.keys()))
    
    base = 'https://clinicaltrials.gov/api/v2/studies'
    
    extract_fields = [
        'NCTId',
        'Condition',
        'OverallStatus'
    ]
    
    statuses = [
        'NOT_YET_RECRUITING',
        'RECRUITING'
    ]
    
    params = {
        #'filter.ids':'NCT05152134',
        'fields': ",".join(extract_fields), 
        'query.locn': 'United States',
        'filter.overallStatus':",".join(statuses),
        'filter.advanced':'AREA[Phase]Phase 3',
        'pageSize': 1000,
        'format': 'json', 
        #'pageToken': None  # first page doesn't need it
    } 
    
    overwrite_keys = ['PK', 'SK']
    
    while True:
        res = requests.get(base, params=params)
                
        if not res.ok:
            return res.text
        
        json_data = res.json() if res and res.status_code == 200 else None
        
        if 'studies' in json_data:
            with table.batch_writer(overwrite_by_pkeys=overwrite_keys) as batch:
                for study in json_data['studies']:
                    for condition in study['protocolSection']['conditionsModule']['conditions']:
                        condition2 = condition.upper()
                        for key_word in conMapKeyList:
                            if key_word in condition2:
                                res2 = batch.put_item(
                                        Item={
                                            'PK':'s#'+conMap.get(key_word),
                                            'SK':'s#'+study['protocolSection']['identificationModule']['nctId'],
                                            'overallStatus':study['protocolSection']['statusModule']['overallStatus']
                                    })
        nextPageToken = json_data.get('nextPageToken')
        if nextPageToken:
            params['pageToken'] = nextPageToken  # Set the pageToken for the next request
        else:
            break  # Exit the loop if no nextPageToken is present               
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }