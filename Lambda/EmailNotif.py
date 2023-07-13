import boto3
import datetime
from dateutil.relativedelta import relativedelta
import math

#Default empty event returned if nothing is passed to the function
empty_event = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

def lambda_handler(event, context):
    k = False
    if event == empty_event:
        k = True
        print("Empty event var.")
    
    #Only run the main code if the data passed to the function is not default empty value    
    if k == False:
        #Set variables for later usage to access AWS resources
        client = boto3.client('ses')
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('EmailList')
        #Retrieve list of email addresses and associated notification preferences
        emailList = table.scan()['Items']
        #Create list to add email addresses to it later which want dog emails
        emailList_dogs = []
        print(emailList)

        #Get passed dict from event and assign to var
        ArrivalsDict = event["responsePayload"]
        print(ArrivalsDict)
        
        #Read list of emails from EmailList table
        #If cats=True then throw out all email addresses only wanting dogs, and vice versa
        #For loop outside of try loop, iterate through all emails
        for emailDict in emailList:
            print(emailDict['comm_medium'])
            print(f"{emailDict['comm_medium']}'s dog value is {emailDict['dogs']}")
            if emailDict['dogs'] == 'true':
                print(f"{emailDict['comm_medium']} does not want dog emails. Removing...")
                emailList_dogs.append(emailDict)
        print(f"emailList_dogs: {emailList_dogs}")
        
        message = """<html>
                     <body>"""
        #Iterate through all items in passed dict to build out the emails
        for dog, DogDict in ArrivalsDict.items():
            #print(DogDict)
            age = DogDict['age']
            if age == 'Senior ':
                continue
            name = DogDict['dog_name']
            breed = DogDict['breed']
            weight = DogDict['weight']
            photo = DogDict['cover_photo']
            url = DogDict['public_url']

            #The birthday of each animal is in UNIX time, so this code converts it to human readable format
            birthday = int(DogDict['birthday'])
            bday = datetime.datetime.fromtimestamp(birthday).date()
            today = datetime.date.today()
            delta = relativedelta(today, bday)
            weeks = math.floor(delta.days / 7)
            age = f"{delta.years}Y/{delta.months}M/{weeks}W"
            
            #Build body and subject of email using previously parsed info from animal dict.
            #Body is formed in HTML for formatting, hyperlink, embedding image purposes
            if len(ArrivalsDict) == 1:
                subject = f"{name} is now available to adopt!"
            else:
                subject = f"There are new dogs available to adopt!"
            
            message+=f"""<img src={photo} alt="dog photo" width="40%" /><br>
                        Name: {name}<br>
                        Age: {age}<br>
                        Breed: {breed}<br>
                        Weight: {weight}<br>
                        Link: {url}<br><br>"""
            
            #Iterate through each email address in dict, if they are requesting email notifs then proceed.
        for emailDict in emailList_dogs:
            if emailDict['comm_type'] == 'email':
                email_address = emailDict['comm_medium']
                try:
                    #Add footer to each email body with custom email address added to unsubscribe link
                    message1 = message
                    footer = f"""<footer>
                                <p><a href="https://rt4jhd7yf5.execute-api.us-east-1.amazonaws.com/unsub?{email_address}">Unsubscribe from this email list.</a></p>
                            </footer>
                            </body>
                            </html>"""
                    message1 += footer

                    print(f"Sending email for {name} to {email_address}")
                    response = client.send_email(
                        Destination={
                            'ToAddresses': [
                                email_address,
                            ],
                        },
                        Message={
                            'Body': {
                                'Html': {
                                    'Charset': 'UTF-8',
                                    'Data': message1,
                                }
                            },
                            'Subject': {
                                'Charset': 'UTF-8',
                                'Data': subject,
                            },
                        },
                        Source='hiring@brandon-daley.com',
                    )
                except Exception as e:
                    print(f"Error: {e}")
                    print("Email send failure.")
            
    return empty_event