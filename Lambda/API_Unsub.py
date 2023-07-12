import json
import boto3

#Set variables for later usage to access AWS resources
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('EmailList')
    
def lambda_handler(event, context):
    unsub = False
    #Grab user email address from query string of API request
    email_address = event['rawQueryString']
    #Format their email as a dict
    email_address_dict = {'comm_medium': event['rawQueryString']}
        
    try:
        emailList = table.scan()['Items']
        for emailDict in emailList:
            #Check if person attempting to unsubscribe is currently subscribed. If they are, delete their info from DB.
            if emailDict['comm_medium'] == email_address:
                unsub = True
                print(f"Deleting {email_address_dict}...")
                table.delete_item(Key=email_address_dict)
    except Exception as e:
        print(f"Error: {e}")
    
    #If the user attempting to unsubscribe was not currently subscribed, return a message to the webpage to notify them.
    #Otherwise, notify them their unsubscription was successful.
    if unsub == True:
        return "You have successfully unsubscribed from all mailing lists."
    else:
        return "You are not currently subscribed to any of our mailing lists."