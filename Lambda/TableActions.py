import boto3

#Default empty event returned if nothing is passed to the function
empty_event = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

def lambda_handler(event, context):
    k = False
    if event == empty_event:
        k = True
    
    #Only run the main code if the data passed to the function is not default empty value
    if k == False:
        #Set variables for later usage to access AWS resources
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('HPA')

        #Access the main data passed from the previous function
        event = event["responsePayload"]
        #Assign each dictionary in the list assigned to {event} to its' own variable.
        ArrivalsDict = event[0] #Dogs that are on website but not in DynamoDB table, i.e. They are new arrivals.
        AdoptedDict = event[1] #Dogs that are in DynamoDB table but not on website, i.e. They've been adopted.
        
        #If this dict is not null iterate through it and delete the animals from the DB which have been adopted
        if AdoptedDict:
            for AdoptedDog in AdoptedDict:
                #AdoptedDog = {'dog_name': AdoptedDog}
                table.delete_item(Key={'dog_name': AdoptedDog})
        
        #If this dict is not null iterate through it and add them to the DB
        if ArrivalsDict:
            for ArrivalDog in ArrivalsDict.items():
                table.put_item(Item=ArrivalDog[1])
            #Return this dict for use in next function
            return ArrivalsDict
        #else, force the lambda to end in a failure state by running an os command without importing the os module
        else:
            os.system('ls')