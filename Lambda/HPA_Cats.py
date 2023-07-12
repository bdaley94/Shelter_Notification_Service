import urllib3
import json
import boto3

#Set variables for later usage to access AWS resources
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('HPA_Cats')

#This function compares returns two dictionaries containing the animals that are new arrivals to the shelter
#and those that have been adopted since the last time the code ran.
def compare_nested_dicts(old_dict, new_dict):
    ArrivalsDict = {}
    AdoptedDict = {}
    #Find dogs that are on website but not in DynamoDB table, i.e. They are new arrivals.
    for key, new_value in list(new_dict.items()):
        if key not in old_dict:
            ArrivalsDict[key] = new_value
    #Find dogs that are in DynamoDB table but not on website, i.e. They've been adopted.
    for key, new_value in list(old_dict.items()):
        if key not in new_dict:
            AdoptedDict[key] = new_value
    return ArrivalsDict, AdoptedDict

def lambda_handler(event, context):
    #Gather initial data on the animals from Shelterluv
    url = 'https://www.shelterluv.com/api/v3/available-animals/5710?species=Cat&embedded=1&iframeId=shelterluv_wrap_1601325792999&columns=1'
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    dog = json.loads(r.data)['animals']

    #Retrieve items from DynamoDB table, add them all to OldDogsDict
    OldDogScan = table.scan()
    OldDogScan = OldDogScan['Items']
    OldDogsDict = {}
    for OldDog in OldDogScan:
        OldDogsDict[OldDog['cat_name']] = OldDog

    #Set dict variable, this will be used to contain the data from the Shelterluv api
    NewDogsDict = {}
    
    #Iterate through each item in the dictionary returned from the api
    for key in dog:
        #Look through all photos and assign cover photo to variable
        for i in key['photos'].items():
            if i[1]['isCover'] == True:
                cover = i[1]['url']
        
        #Parse out all the data that I will be using
        NewDog = {
            'cat_name': key['name'],
            'nid': key['nid'],
            'age': key['age_group'],
            'breed': key['breed'],
            'secondary_breed': key['secondary_breed'],
            'sex': key['sex'],
            'weight': f"{key['weight']} lbs",
            'cover_photo': cover,
            'public_url': key['public_url'],
            'birthday': key['birthday']
        }
        #Add the newly parsed dict for each animal to NewDogsDict as sub dictionaries of the dogs name
        NewDogsDict[key['name']] = NewDog
        
    ArrivalsDict, AdoptedDict = compare_nested_dicts(OldDogsDict, NewDogsDict)
    
    #If either dictionary is not empty, return them for use in the next function
    #else, I forced the lambda to end in a failure state by running an os command without importing the os module
    if ArrivalsDict or AdoptedDict:
        return ArrivalsDict, AdoptedDict
    else:
        os.system('ls')
