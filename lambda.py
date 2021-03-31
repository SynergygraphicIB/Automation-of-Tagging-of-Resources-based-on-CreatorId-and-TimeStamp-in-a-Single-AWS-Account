import json
import boto3
import re
from datetime import datetime, date, time, timezone

datenow= datetime.now()
now= datenow.strftime("%Y-%m-%d %H:%M:%S")

def lambda_handler(event, context):
    
    # it overwrites event variable with the event coming from previous lambda
    event= json.loads(event['Records'][0]['Sns']['Message'])
    
    # We capture and Filter the evenName -  if not a creation event it does not process the tag Creator
    # if itis a  creation event it does process the tag Creator, it passes the event, userIdentity and awsRegion coming from json
    
    eventName=event["detail"].get("eventName")
    
    roleARN= "arn:aws:iam::"+str(event.get("account"))+":role/AutoTaggingExecuteLambda"
    
    region=event["detail"].get("awsRegion")
    userName = event["detail"]["userIdentity"].get("sessionContext")
    principaID= event["detail"]["userIdentity"].get("arn")
    
    if(userName != None):
        userName= userName["sessionIssuer"].get("userName")
    else:
        userName= event["detail"]["userIdentity"].get("userName")
    

    #CreateStack
    if(eventName == "CreateStack"):
        cloudformation = boto3.client('cloudformation' , region_name = region)
        stack= event["detail"]["requestParameters"].get("stackName")
        url = event["detail"]["requestParameters"].get("templateURL")
        addTagStack(cloudformation,userName,principaID, stack , url)
    

    #ParameterStore
    elif(eventName == "PutParameter"):
        resourcegroupstaggingapi= boto3.client('resourcegroupstaggingapi' , region_name = region)
        projectArn= event["detail"]["resources"][0]["ARN"]
        addtagResource(resourcegroupstaggingapi,userName,principaID, projectArn)
    

    #Pipeline
    elif(eventName == "CreatePipeline"):
        resourcegroupstaggingapi= boto3.client('resourcegroupstaggingapi' , region_name = region)
        codepipeline= boto3.client('codepipeline' , region_name = region)
        codepipelineArn= event["detail"]["responseElements"]["pipeline"].get("name")
        responsepipeline= codepipeline.get_pipeline(name = codepipelineArn)
        codepipelineArn = responsepipeline["metadata"].get("pipelineArn")
        addtagResource(resourcegroupstaggingapi,userName,principaID, codepipelineArn)
    

    #CodeBuild
    elif(eventName == "CreateProject"):
        resourcegroupstaggingapi= boto3.client('resourcegroupstaggingapi' , region_name = region)
        projectArn= event["detail"]["requestParameters"].get("name")
        addtagResource(resourcegroupstaggingapi,userName,principaID, projectArn)
     
    #CLOUDTRAIL
    elif(eventName == "CreateTrail"):
        clientTrail= boto3.client('cloudtrail' , region_name = region)
        trailArn= event["detail"]["responseElements"].get("trailARN")
        addTagTrail(clientTrail,userName,principaID, trailArn)
                

    #TOPIC SQS
    elif(eventName == "CreateQueue"):
        resourcegroupstaggingapi= boto3.client('resourcegroupstaggingapi' , region_name = region)
        queueArn= event["detail"]["requestParameters"].get("queueName")
        queueArn = "arn:aws:sqs:"+region+":" +str(event.get("account"))+":"+queueArn
        addtagResource(resourcegroupstaggingapi,userName,principaID, queueArn)    
    #TOPIC SNS
    elif(eventName == "CreateTopic"):
        resourcegroupstaggingapi= boto3.client('resourcegroupstaggingapi' , region_name = region)
        topicArn= event["detail"]["responseElements"].get("topicArn")
        addtagResource(resourcegroupstaggingapi,userName,principaID, topicArn)
    #LAMBDA    
    elif(eventName == "CreateFunction20150331"):
        functionArn=event["detail"]["responseElements"]
        if(type(functionArn) == dict):
            functionArn=functionArn.get("functionArn")
            print(functionArn)
            resourcegroupstaggingapi= boto3.client('resourcegroupstaggingapi' , region_name = region)
            addtagResource(resourcegroupstaggingapi,userName,principaID, functionArn)
        else:
            print("NO ")
            
    #CLOUDWATCH
    elif(eventName == "PutRule"):
        resourcegroupstaggingapi= boto3.client('resourcegroupstaggingapi' , region_name = region)
        ruleArn= event["detail"]["responseElements"].get("ruleArn")
        addtagResource(resourcegroupstaggingapi,userName,principaID, ruleArn)
        
    elif(eventName == "CreateLogGroup"):
        resourcegroupstaggingapi= boto3.client('logs' , region_name = region)
        logArn= event["detail"]["requestParameters"].get("logGroupName")
        addtagLogGruop(resourcegroupstaggingapi,userName,principaID, logArn)
    #IAM
    elif(eventName == "CreateUser"):
        iam= boto3.client('iam' , region_name = region)
        userNamec= event["detail"]["responseElements"]["user"].get("userName")
        addTagUser(iam,userName,principaID, userNamec)

    elif(eventName == "CreateRole"):
        iam= boto3.client('iam' , region_name = region)
        roleName= event["detail"]["responseElements"]["role"].get("roleName")
        addTagRole(iam,userName,principaID, roleName)
    
    elif(eventName =="CreatePolicy"):
        iam= boto3.client('iam' , region_name = region)
        PolicyArn= event["detail"]["responseElements"]["policy"].get("arn")
        addTagPolicy(iam,userName,principaID, PolicyArn)
    #S3
    elif(eventName == "CreateBucket"):
        resourcegroupstaggingapi= boto3.client('resourcegroupstaggingapi' , region_name = region)
        bucket_name= event["detail"]["requestParameters"].get("bucketName")
        bucket_name ="arn:aws:s3:::"+bucket_name
        addtagResource(resourcegroupstaggingapi,userName,principaID, bucket_name)
        
    elif(eventName == "PutObject"):    
        resourcegroupstaggingapi= boto3.client('s3' , region_name = region)
        obj= event["detail"]["resources"][0]["ARN"]
        bucket_name= event["detail"]["requestParameters"].get("bucketName")
        bucket_arn ="arn:aws:s3:::"+bucket_name
        file = obj.split(bucket_arn+"/")[1] 
        addTagObjt(resourcegroupstaggingapi,userName,principaID, bucket_name,file)

    #EC2
    elif("Create" in eventName or (eventName in ["RunInstances","AllocateAddress"])):
        
        client = boto3.client('ec2', region_name = region )
        response =  event["detail"]["responseElements"]
        request = event["detail"]["requestParameters"]
    
        request_ids=[]
        response_ids = []
        
        for request_id in item_generator(request):
            request_ids.append(request_id)
            
        for response_id in item_generator(response):
            if (response_id not in request_ids):
                if(eventName == "RunInstances" and "vpc-" not in response_id):
                    response_ids.append(response_id)
                elif(eventName != "RunInstances"):
                    response_ids.append(response_id)
        
        for ids in response_ids:
            addTagClient(client,userName,principaID, ids)
    else:
        return "Not is event creation"

# addTagClient - function to create tags in all resources newly created
# it adds the value principalID to creatorID tag to each resource created
def addTagClient(client,userName,principaID, ids):
    try:
        response = client.create_tags(
            Resources=[
                ids,
            ],
            Tags=[
                {
                    'Key': 'creatorId',
                    'Value': principaID,
                },
                {
                    'Key': 'UserName',
                    'Value': userName,
                },
                {
                    'Key': 'create_at',
                    'Value': now
                },
            ],
        )
    except Exception as e:
        print (e)
        
        
        
        
def addTagStack(client,userName,principaID, ids, url):
    try:
        response = client.update_stack(
            StackName= ids,
            TemplateURL = url,
            Tags=[
                {
                    'Key': 'creatorId',
                    'Value': principaID,
                },
                {
                    'Key': 'UserName',
                    'Value': userName,
                },
                {
                    'Key': 'create_at',
                    'Value': now
                },
            ],
        )
    except Exception as e:
        print (e)        
        
def addTagTrail(client,userName,principaID, ids):
    try:
        response = client.add_tags(
            ResourceId= ids,
            TagsList=[
                {
                    'Key': 'creatorId',
                    'Value': principaID,
                },
                {
                    'Key': 'UserName',
                    'Value': userName,
                },
                {
                    'Key': 'create_at',
                    'Value': now
                },
            ],
        )
    except Exception as e:
        print (e)
                

def addTagRole(client,userName,principaID, rolename):
    try:
        response = client.tag_role(
            RoleName=rolename,
            Tags=[
                {
                    'Key': 'creatorId',
                    'Value': principaID,
                },
                {
                    'Key': 'UserName',
                    'Value': userName,
                },
                {
                    'Key': 'create_at',
                    'Value': now
                },
            ],
        )
    except Exception as e:
        print (e)
        
def addTagUser(client,userName,principaID, username):
    try:
        response = client.tag_user(
            UserName=username,
            Tags=[
                {
                    'Key': 'creatorId',
                    'Value': principaID,
                },
                {
                    'Key': 'UserName',
                    'Value': userName,
                },
                {
                    'Key': 'create_at',
                    'Value': now
                },
            ],
        )
    except Exception as e:
        print (e)
        

def addTagPolicy(client,userName,principaID, policy):
    try:
        response = client.tag_policy(
            PolicyArn= policy,
            Tags=[
                {
                    'Key': 'creatorId',
                    'Value': principaID,
                },
                {
                    'Key': 'UserName',
                    'Value': userName,
                },
                {
                    'Key': 'create_at',
                    'Value': now
                },
            ],
        )
    except Exception as e:
        print (e)

                
def item_generator(json_input):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if(type(v)== str):
                if re.match('^[(a-z)]+-[(a-z0-9)]',v.lower()) and "Id" in k : 
                    if (k not in ("requestId","reservationId","ownerId","attachmentId","associationId")):
                        yield v
            else:
                yield from item_generator(v)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from item_generator(item)
            

def addtagResource(resourcegroupstaggingapi,userName,principaID, arn):
    try:
        resourcegroupstaggingapi.tag_resources(
            ResourceARNList=[
                arn,
            ],
            Tags={
                'creatorId': principaID,"UserName":userName,"create_at":now
            }
        )
    except Exception as e:
        print (e)
        
def addtagLogGruop(client,userName,principaID, arn):
    try:
        client.tag_log_group(
            logGroupName= arn
            ,
            tags={
                'creatorId': principaID,"UserName":userName,"create_at":now
            }
        )
    except Exception as e:
        print (e)
        

        
        
def addTagObjt(client,userName,principaID, ids ,file):
    try:
        response = client.put_object_tagging(
            Bucket=ids,
            Key=file,
            Tagging={
                  'TagSet' : [
                    {
                        'Key': 'creatorId',
                        'Value': principaID,
                    },
                    {
                        'Key': 'UserName',
                        'Value': userName,
                    },
                    {
                        'Key': 'create_at',
                        'Value': now
                    },
                ]
                
            },
        )
    except Exception as e:
        print (e)
