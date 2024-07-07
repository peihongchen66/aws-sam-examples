import requests
import boto3

def lambda_handler(event, context):
    res = requests.get(
            url='https://clinicaltrials.gov/api/v2/studies?filter.ids=NCT05305911',
            headers={'Accept': 'application/json'},
            timeout=5)
            
    print(type(res))
        
    json_data = res.json() if res and res.status_code == 200 else None
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('StudyDynamoTable') 
    
    if 'studies' in json_data:
        for study in json_data['studies']:
            for condition in study['protocolSection']['conditionsModule']['conditions']:
                print(condition)
                res2 = table.put_item(
                    Item={
                        'PK':'s#'+condition,
                        'SK':'s#'+study['protocolSection']['identificationModule']['nctId'],
                        'briefTitle':study['protocolSection']['identificationModule']['briefTitle'],
                        'overallStatus':study['protocolSection']['statusModule']['overallStatus']
                    })
  
   
    return res2