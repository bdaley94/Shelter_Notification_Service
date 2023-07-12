import json
import boto3

#Set variables for later usage to access AWS resources
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('EmailList')
responseObject = {}
        
def lambda_handler(event, context):
    #Retrieve form data from website form
    event = json.loads(event['body'])
    print(event)
    
    try:
        #Check if the submitted email address/phone # already exists in DB
        response = table.get_item(Key={'comm_medium': event['comm_medium']})
        #If it already exists, append item to responseObject noting their settings will be updated. This is referenced in my JS code.
        if response['Item']:
            responseObject["Update"] = "true"
    except Exception as e:
        responseObject["Update"] = "false"
        print(e)
        pass

    try:
        #Add form data dict to DB, return 200 status code if successful
        table.put_item(Item=event)
        responseObject["statusCode"] = 200
    except Exception as e:
        print(e)
        responseObject["statusCode"] = 500
    
    #Format responseObject as string for transfer between Python/JS code
    js_ready_responseObject = str(responseObject).replace("'", "\"")
    return js_ready_responseObject
    