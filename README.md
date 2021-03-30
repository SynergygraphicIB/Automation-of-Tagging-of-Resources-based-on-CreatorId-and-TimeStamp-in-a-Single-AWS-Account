# Automatization for Tag Creation with the Username ARN and ID:
This is an open-source solution to do **AutoTagging** for newly deployed resources using `CloudTrail` and `EventBridge` to route the event to a endpoint - a `lambda function` It will do its task  `to tag resources` at the moment of creation with the arn of who created, the username ID, and the time of creation. 
Insofar we have the following services sucessfully tested for auto-tag creation; `all ec2 services, S3, CloudTrail, CloudWatch, System Manager, Code Pipeline, CodeBuild, Sns, Sqs, IAM, and Cloudformation`. Each of those services get a set of tags with Creator ID, the ARN, and Timestamp of Creation.

### PreFlight Check
1. Intermedial level in Python. So you can adapt and customized the `Lambda.py` file to your needs
2. Basic to intermedial understanding about how to edit json policies in `EventBridge Rules` to change the rule basde on your use cases since we have not covered every single resource in AWS.
3. One AWS Account to deploy Auto-Tagging **Lambda function** and to launch AWS resources.
4. In the AWS Account we must include:
    A. `Cloudwatch` log group collecting `cloudtrail` for every region.
    B. A `Eventbridge rule` for every region that we want to include in the tag automatizaton of newly deployed resources.
    C. A `SNS Topic` for everyt region to send the Event Data to the Auto-tagging lambda function.
    D. A `Lambda Function` in us-east-1 as endpoint to do the tagging.

## List of Resources that can be tagged.
1. EC2 Resources
2. S3
3. IAM
4. CloudTrail
5. Cloudwatch
6. System Manager
7. Code Pipeline
8. CodeBuild
9. SNS Topics
10. SQS

### One existing AWS Account
An existing AWS account that for the purpose of this exercise we will have an Id 111111111111. We are going to deploy AWS resources in us-east-1, action which will create an event. This event will be sent through a pipeline that will have as endpoint the **lambda autotagging** in us-east-1. Thus fulfilling the purpose of centralizing auto-tagging for the listed events coming from any region linked to the lambda.

### IAM Role

**ExecuteAutoTaggingLambda** - Role we create with a limited access policy to enable the lambda to execute the tagging of newly deployed resources. This is the role will have to polices attached; the aws mananged basic lambda execution policy

See `AutoTaggingExecuteLambdaPolicy.json`
or copy paste from here...
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "tag:*",
                "resource-explorer:*",
                "iam:TagPolicy",
                "iam:TagInstanceProfile",
                "iam:UntagPolicy",
                "iam:UntagOpenIDConnectProvider",
                "iam:UntagInstanceProfile",
                "iam:TagOpenIDConnectProvider",
                "iam:TagMFADevice",
                "iam:TagSAMLProvider",
                "iam:UntagSAMLProvider",
                "iam:TagRole",
                "iam:UntagRole",
                "iam:UntagServerCertificate",
                "iam:TagUser",
                "iam:UntagUser",       
                "iam:UntagMFADevice",
                "iam:TagServerCertificate",
                "ec2:CreateTags",
                "ec2:DeleteTags",
                "s3:DeleteJobTagging",
                "s3:PutObjectTagging",
                "s3:DeleteObjectTagging",
                "s3:DeleteStorageLensConfigurationTagging",
                "s3:DeleteObjectVersionTagging",
                "s3:ReplicateTags",
                "s3:PutBucketTagging",
                "s3:PutStorageLensConfigurationTagging",
                "s3:PutObjectVersionTagging",
                "s3:PutJobTagging",      
                "sqs:TagQueue",
                "sqs:UntagQueue",
                "sns:TagResource",
                "sns:UntagResource",
                "logs:*",
                "cloudtrail:AddTags",   
                "cloudtrail:RemoveTags",
                "cloudformation:UpdateTerminationProtection",
                "cloudformation:TagResource",
                "cloudformation:UntagResource",             
                "cloudformation:CreateChangeSet",
                "cloudformation:UpdateStackSet",
                "cloudformation:UpdateStack",
                "cloudformation:UpdateStackInstances",
                "codebuild:UpdateProject",
                "codebuild:BatchGetProjects",
                "codepipeline:GetPipeline",
                "codepipeline:ListTagsForResource",
                "codepipeline:UntagResource",
                "codepipeline:CreatePipeline",
                "codepipeline:CreateCustomActionType",
                "codepipeline:TagResource",
                "codepipeline:PutWebhook",
                "ssm:RemoveTagsFromResource",
                "ssm:GetParameters",
                "ssm:AddTagsToResource",
                "ssm:ListTagsForResource",
                "mediastore:TagResource",
                "mediastore:UntagResource"  
            ],
            "Resource": "*"
        }
    ]
}
```
### EventBridge Rule
**EventAutoTaggingRule** - This rule filters create or launch events coming from `AWS API Call via CloudTrail` that start with the prefix `"Create"` and `"Put"` and `RunInstances`; which is the one to launch a new EC2 instance, and `"AllocateAddress"` for creating an Elastic IP Adress. We used Prefix Matching feature in order to reduce the need to update and rewrite the rule written in json format  . There are about 650 create events for the different aws services and about 147 put events that start with Create or PUt so our rule may need little if nothing updating and upgrading to cover new events launched by AWS.

```json
{
  "detail-type": [
    "AWS API Call via CloudTrail"
  ],
  "detail": {
    "eventName": [
      {
        "prefix": "Create"
      },
      {
        "prefix": "Put"
      },
      "RunInstances",
      "AllocateAddress"
    ]
  }
}
```

We will create a rule for every region in the account that we want to include in the **Auto Tagging** lambda function in us-east-1

### Sns Topics
**SnsSendToLambda** - The `SNS Topic` that have to be created in every region of the account where we want to do deployments.  This `SNS Topic` helps to centralize the collection of creation events from all regions and sends the event metadata to us-east-1 to the **Autotagging lambda**, the one function that does the auto tagging throughout the account. We set this `SNS Topic` it as target for rule **"EventAutoTagging"** rule in `EventBridge` in order to pass the event to lambda (then again from any region). Sns is one of the few AWS services that can deliver event data across regions, so in order to make our pipeline as scalable as possible we use `SNS Topics` as intermedial step in te pipeline.
In our project a `EventBridge Rule` could be deployed in us-east-2 or us-west-1 and stil relay the event using `SNS Topic` as target to pass events to the lambda function in us-east-1 region.

### Lambda function

**AutoTagging** - Lambda function that we deploy in the *Receiver Account* in the us-east-1 region. First, It converts the event coming from `SNS Topic`  **"AutoTaggingSNS"** in a form of a string back into `json` format. Then following a series of validations adapted to every creation case, it creates Tags with the creator ID, the ARN, and the time stamp to track who did what and when. This is a highly valuable feature to help keep tracking resources and reduce the time consuming resource management. In summary, the lambda  is deployed in *Receiver account* in us-east-1 region and again it is triggered by `SNS Topic` **"AutoTaggingSNS**". whenever a creation event happens for the validated AWS Services in the function.

## How does it work this pipeline? 
In the chosen AWS account the lambda **"AutoTagging"** function is fired when any AWS resource is us-east-1 either by using the console or the AWS SDK for Python (Boto3). The newly deployed resource gets three tags: User Name, Creator ID, and Create at. Tags which are the basis for any good resource cost control and managment.

A Vpc is launched in us-east-1, and event though the **Auto-tagging** lambda function is in also in us-east-1 this pipeline setting is scalable to automate auto-tagging for any region in the account. Once you set the this pipleline for a chosen region the creation or deployment event that happen in that region will have their tags done by the **AutoTagging** lambda function in us-east-1 . 
At the moment of deployment, say a VPC, an event metadata is generated. Date of creation, who was the creator, ARN of the creator, etc. Thus the meta data is passed from the original point - us-east-1  to lambda function in us-east-1 to the auto-tagging lambda function to do the tagging.
A VPC is launched in us-east-1
`AWS CloudTrail` in us-east-1 records API activity and logs the creation event - `"CreateVpc`". 
The Amazon EC2 CreateVpc API CloudTrail event provides a lot of tagging information. For example:
```
User ID of the entity that created the resource from the principalId key
The IAM role the entity assumed during resource creation from the arn key.
The date/time of resource creation from the eventTime key.
The Vpc ID and other metadata contained in the event. 
```

Then, `EventBridge` filters the creation event base on **EventAutoTaggingRule.** This rule looks for any event that has `"Create"` as a prefix"  and sends the metadata event to SNS Topic "SNSToAutoTaggingMasterLambda"

**SNSToAutoTaggingMasterLambda** passes the event to The **AutoTagging lambda function** in a form of string. 

**Autotagging lambda function** is fired. firstly converts the string into a `json` readable format. Then by sorting the metada data by type of event it determines what "if " statement have to the tagging.
In Summary, The purpose of this pipeline is to centralize the control and tagging of resources being deployed from any region of the account. It reduces the human error factor at the moment of resource tagging.

Following this configuration we can repeat the same process for the other regions that we want to include in the **autotagging.** in the account 

By using *SNS Topics* as intermedial step in the pipeline allow us to modify this function to automate tagging from a single to multiple accounts with very little modifications. We have a separate Git where we explain how you can do the autotagging across accounts.

When using the prefix matching feature in EventBridge we can reduce the amount of written code when creating the filters and we may reduce the updating as well. 
EventBridge and CloudWatch services sort of overlap each other. Yet you can create custom rules in EventBridge that you cannot do in CloudWatch. Therefore, we configure the customed rules in EventBridge, yet the end result is also shown in CloudWatch. The funny thing when updating the very same rules in CloudWatch directly we get an error message, it just does not work in CloudWatch. 

# 1. Log in into you account 
Log in into the console of your existing AWS Account.
For most purposes we are going to use  us-east-1 as chose region for this project. Some AWS Service are global, such as; `Access Management (IAM)` and `S3`. Yet, `Cloudwatch`, `EventBridge`, `SNS Topics`, and `Lambda` are regional.

# 2 IAM- Setting up a Role with the appropiate permsissions to execute Lambda functions
Create a role and a policy that has enough permissions to execute the auto-tagging lambda function and to tag resources

#### Create a policy to autorize **ExecuteAutoTaggingLambda** role to tag resources
a.- At the console screen go to services and type in the text box `"IAM"` or under All
    ```Services > Security, Identity, & Compliance > IAM```
b.- In `Identity and Access Managment (IAM) menu > go to Policies` and click `"Create policy"` button
c.- Click Create policy next.
d.- In Create policy window select JSON tab. Click and paste the following policy and click the "Next: tags" button:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "tag:*",
                "resource-explorer:*",
                "iam:TagPolicy",
                "iam:TagInstanceProfile",
                "iam:UntagPolicy",
                "iam:UntagOpenIDConnectProvider",
                "iam:UntagInstanceProfile",
                "iam:TagOpenIDConnectProvider",
                "iam:TagMFADevice",
                "iam:TagSAMLProvider",
                "iam:UntagSAMLProvider",
                "iam:TagRole",
                "iam:UntagRole",
                "iam:UntagServerCertificate",
                "iam:TagUser",
                "iam:UntagUser",       
                "iam:UntagMFADevice",
                "iam:TagServerCertificate",
                "ec2:CreateTags",
                "ec2:DeleteTags",
                "s3:DeleteJobTagging",
                "s3:PutObjectTagging",
                "s3:DeleteObjectTagging",
                "s3:DeleteStorageLensConfigurationTagging",
                "s3:DeleteObjectVersionTagging",
                "s3:ReplicateTags",
                "s3:PutBucketTagging",
                "s3:PutStorageLensConfigurationTagging",
                "s3:PutObjectVersionTagging",
                "s3:PutJobTagging",      
                "sqs:TagQueue",
                "sqs:UntagQueue",
                "sns:TagResource",
                "sns:UntagResource",
                "logs:*",
                "cloudtrail:AddTags",   
                "cloudtrail:RemoveTags",
                "cloudformation:UpdateTerminationProtection",
                "cloudformation:TagResource",
                "cloudformation:UntagResource",             
                "cloudformation:CreateChangeSet",
                "cloudformation:UpdateStackSet",
                "cloudformation:UpdateStack",
                "cloudformation:UpdateStackInstances",
                "codebuild:UpdateProject",
                "codebuild:BatchGetProjects",
                "codepipeline:GetPipeline",
                "codepipeline:ListTagsForResource",
                "codepipeline:UntagResource",
                "codepipeline:CreatePipeline",
                "codepipeline:CreateCustomActionType",
                "codepipeline:TagResource",
                "codepipeline:PutWebhook",
                "ssm:RemoveTagsFromResource",
                "ssm:GetParameters",
                "ssm:AddTagsToResource",
                "ssm:ListTagsForResource",
                "mediastore:TagResource",
                "mediastore:UntagResource"  
            ],
            "Resource": "*"
        }
    ]
}
```

# 3. Lambda- Deploy Autotagging Lambda Function in us-east-1

We set our lambda function in virginia region/ us-east-1. This is the endpoint for any deployment or creation event happening in any region in that is configured in the pipeline for **Auto-tagging* and in this lambda function. 

Create a **AutoTagging** lambda function with the console:

a.- First, be sure you are in us-east-1 . In the console click the services tab and look for Lamdba under; 
```
All services > Compute > Lambda or just type lambda in the text box. then hit Lambda
```
b.- In the AWS lambda window go to Functions.
c. Click the "Create function" buttom.
d. You will the following options to create your function Author from scratch, Use blueprint, Container Image, and Browse serverless app repository, choose Author from scratch.
e. In Function name type **"AutoTagging"** or any name you choose to, in Runtime look for Python 3.8
f.- In Permissions - click Change default execution role and select "Use an existing role". In the dialog box that opens up look for **ExecuteAutoTaggingLambda**, this is the role we created in the previous step.
g.- Click "Create function" button
h.- Under Code source > In Environment click `lambda_function.py`
i.- Delete all existing code an replace it with the code provided in the `Lambda.py` file
j.- Once you paste the new code click "Deploy"
j.- In the Code Source menu click Test
k.- In Configure test event leave Create new test event selected, In event name type create_tags and click "Create Test" Button

{pegar imagen aqui}

# 4. SNS Topics - Create a Topic and publish to a lambda function
Create a topic - **"SNStoAutoTaggingLambda"** and Subscribe it to Lambda Function **"AutoTagging"** *in us-east-1*. So let us follow the next steps:

a.- Be sure you are in us-east-1 region (SNS works across regions, but still is a regional resource)
b.- At the console screen go to services and type in the text box "sns" or under All ```
```
services > Aplication Intergration > Simple Notification Service
```
c. -CLick at the Simple Notification Service
e.- In the menu to the left click Topics and then The `"Create Topic"` orange buttom.
f.- In Create topic window choose Stardard, In Name type **"SNStoAutoTaggingLambda"**
g.- In the Access policy section we keep the Basic method 
h.- Click Create topic buttom. The topic is created.
i.- Now, we create the subscription. Click the Create subscription button.
j. In Details > Topic ARN look for the topic created in the previous steps
k.-In Protocol choose AWS Lambbda and look for the ARN of the lambda function **AutoTagging.**
l.- Hit the Create Subscription Button. Voila! the subscription is done.

{pegar imagen aqui}

# 5. Amazon EventBridge -  Create an EventBridge Rule in us-east-1 and use as target SnsSendToLambda.
Create a rule that captures all creation events in `Sender Acccount` using `AWS API Call via CloudTrail` and select **SnsSendToLambda** as target:
a.- Be sure you are in `us-east-1` 
b.- At the console screen go to services and type in the text box `"EventBridge"` or under
```All services > Application Integration > Amazon EventBridge```
c.- In the Amazon EventBridge menu select Rules and click "Create Rule" button
d.- Under Name and Description > Name type **"EventAutoTaggingRule**"
e.- Add a Description **"Rule to send creation events to SnsSendToLambda"** if you choose to, it is optional
f.- In Define pattern choose ```"Event pattern" > Custom Pattern```
g.- Copy paste the following json in Event Pattern Dialog Box
```json
{
  "detail-type": [
    "AWS API Call via CloudTrail"
  ],
  "detail": {
    "eventName": [
      {
        "prefix": "Create"
      },
      {
        "prefix": "Put"
      },
      "RunInstances",
      "AllocateAddress"
    ]
  }
}
```
...and click "Save"

h.- In Select` Targets > in Target click the text box, scroll up and select "SNS Topic"`
i.- In Topic text box select **"SnsSendToLambda"**
j.- Click `"Create Rule" `button. 

{pegar imagen aqui}

# 6. Deploy a VPC in us-east-1 and Check the Tags
Either by console or by AWS CLi SDK for boto3 deploy a Vpc or any resource that you desire.
Using the AWS Console:
a. In us-east-1 go to the resource tab
b. In the services search text box type vpc or under "Networking & Content Delivery" look for VPC. Click VPC
c.- In the menu to the left click "Your VPCs"
d.- In Your VPCs window click "Create VPC" button
e.- In Create VPC > VPC settings > Name tag type test-project or any name you want to.
f.- In IPv4 CIDR block type 10.0.0.0/24, leave the rest of the settings as it is.
g.- Click the "Create VPC" button.
{pegar imagen aqui}
h.- You will be redirected to the newly created vpc window details. under the "Tags" tab click it and check for the tags. 

![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/11.png)

You will see the Following tags; create_at, UserName, Name, and creatorId in your newly deployed VPC.

Erase the VPC deployed erased and if you have any comments write to us if you have any comments, suggestions, critics, etc at contact@synergygraphics.io!

### Note: To implement the function in different regions, repeat steps 4 and 5 and replace the region values as applicable
