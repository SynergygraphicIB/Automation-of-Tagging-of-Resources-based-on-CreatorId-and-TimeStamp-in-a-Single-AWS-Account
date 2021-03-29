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

**AutoTaggingExecuteLambda** - Role we create with a limited access policy to enable the lambda to execute the tagging of newly deployed resources. This is the role will have to polices attached; the aws mananged basic lambda execution policy

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

### Event Buses Permissions in CloudWatch
**Add Permissions in Event Buses** - 
`CloudWatch` has a default Event Bus. It is stateless, it means that we have to set the permissions for it to start to receive events from the organization. Therefore, we add the Permissions to get all events from any linked account in the organization. Then Default event bus will accept events from AWS services, `PutEvents API calls` coming from these authorized accounts. 

In Addition, We must also manage permissions on the default event bus of the *linked account* to authorize it to share their events with the *Receiver Account* and to add it as as a target to the rules in in `EventBridge`. 

## We need to add permissions for this particular architecture in Event Buses but Why? 
`Cloudwatch` events only passes events between matching regions across accounts, in this case between *linked account/ us-east-1* and *Receiver Account / us-east-1*. Then, when a Vpc deployment happens in us-east-1 in the *linked account*, this event is then captured by `cloudwatch event buses` and it is passed "through the bus" to a the event bus in `CloudWatch` in *Receiver Account* in us-east-1 as well.

We have to do this permission setting from every region we want to incorporate in the autotagging process and that is why we use the organization, to reduce the modifications needed in the *receiver account*. Once we set the permissions in a certain region in *receiver account* it is ready to pass events from any *linked account* in the organization, instead adding each new account at once.

### Lambda function

**AutoTagging** - Lambda function that we deploy in the *Receiver Account* in the us-east-1 region. First, It converts the event coming from `SNS Topic`  **"AutoTaggingSNS"** in a form of a string back into `json` format. Then following a series of validations adapted to every creation case, it creates Tags with the creator ID, the ARN, and the time stamp to track who did what and when. This is a highly valuable feature to help keep tracking resources and reduce the time consuming resource management. In summary, the lambda  is deployed in *Receiver account* in us-east-1 region and again it is triggered by `SNS Topic` **"AutoTaggingSNS**". whenever a creation event happens for the validated AWS Services in the function.

## How does it work this pipeline? 
The lambda **"AutoTagging"** function in *Receiver Account* is fired when any AWS resource is deployed by *Sender* or *linked account* either by using the console or the AWS SDK for Python (Boto3). The newly deployed resource gets three tags: User Name, Creator ID, and Create at. which are the basis for any good resource cost control and managment.

A Vpc is launched in us-east-1 in *Linked Account*, yet the **Auto-tagging** lambda function is in *Receiver Account* in us-east-1. No matter what creation or deployment event happens, all tagging is going to be done by the **AutoTagging** lambda function . Hence, at the moment of deployment a metadata is generated. Date of creation, and who was the creator, ARN of the creator, etc. Thus the meta data is passed from the original point - *linked account* 222222222222 to lambda function in *receiver account* to do the tagging.

`AWS CloudTrail` in *sender account* 222222222222 records API activity and logs the creation event - `"CreateVpc`". 
The Amazon EC2 CreateVpc API CloudTrail event provides a lot of tagging information. For example:
```
User ID of the entity that created the resource from the principalId key
The IAM role the entity assumed during resource creation from the arn key.
The date/time of resource creation from the eventTime key.
The Vpc ID and other metadata contained in the event. 
```

Then, `CloudWatch` filters the creation event base on **EventAutoTaggingRule.** This rule looks for any event that has `"Create"` as a prefix"  and sends the metadata event to the default event bus that is connected to the event bus in *Receiver Account* - in us-east-1 as well. 

Now the metadata of the event is in  the default bus in *Receiver Account*. After `CloudWatch` filters and matches the event by a matching rule and sends it to **SNSToAutoTaggingMasterLambda**.

**SNSToAutoTaggingMasterLambda** passes the event to The **AutoTagging lambda function** in a form of string. 

**Autotagging lambda function** is fired. firstly converts the string into a `json` readable format. Then by validating the metada data, it determines what kind of create event happened and does the tagging accordingly 

In Summary, The purpose of this pipeline is to centralize the control and tagging of resources being deployed in any *linked account* of the organization. It reduces the human error factor at the moment of tagging.

Following this configuration we can repeat the same process for the other regions in any other linked accounts within the organization that we want to include in the **autotagging.**

By using *SNS Topics* as intermedial step in the pipeline allow us to modify this function to automate tagging from a single to multiple accounts with very little modifications. We have a separate Git where we explain how you can do the autotagging in a single account.
When using prefix feature to create rules we did use EventBridge. When applying or even updating the same rules in CloudWatch directly, it did not work. Hence, we configure the rules in EventBridge and the end result is also shown in CloudWatch. 

# 1. Log in into you account designated as Receiver Account 
This is the account we are going to use to centralized the **Autotagging** for any linked Account. 

Be sure you are in US East (N. Virginia) us-east-1 for most of the purposes of this project, though some AWS Services are global, among those Identity and `Access Management (IAM)` and `S3`.

# 2 Setting up a Role in ReceiverAccount with the appropiate permsissions to execute Lambda functions and to Assume a Role in linked Account
Create a role in *Receiver Accoun*t that has enough permissions to execute lambda the auto-tagging lambdafunction and to assume tag creation role in *Linked Account*. 
Follow the steps:
**Create a Policy **"AssumeLinkedRolePolicy"** to allow AutoTaggingMasterLambda role in receiver account  to assume any role named AWSLambdaBasicExecutionRole in any **Linked account *
a.- Be sure you are in *Receiver Account* 111111111111
b.- At the console screen go to services and type in the text box `"IAM"` or under All
    ```Services > Security, Identity, & Compliance > IAM```
c.- In `Identity and Access Managment (IAM) menu > go to Policies` and click `"Create policy"` button
d.- Click Create policy next.
e.- In Create policy window select JSON tab. Click and paste the following policy and click the "Next: tags" button:

```json
{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Resource": "arn:aws:iam::*:role/AutoTaggingExecuteLambda"
    }
}
```

h.- Click "Next: Review" button
i.- In Review policy window in Name type **"AutoTaggingMasterLambdaPolicy"**
j.- In Description type "Rule to enable **AutoTaggingMasterLambda** Role to assume any role named "AutoTaggingExecuteLambda" in any linked account" and click "Create policy"

![alt text](https://github.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/blob/main/img/1.png?raw=true)





#### Create AutoTaggingMasterLambda role in receiver account
a.- Be sure you are in `Receiver Account` 111111111111
b.- At the console screen go to services and type in the text box `"IAM"` or under All services > Security, Identity, & Compliance > IAM
d.- In Create Role window > Under "Select type of trusted entity" keep AWS service as your choice
e.- In "Choose a use case" select "Lambda" and click "Next: Permissions" button
f.- In next window, under Attach Permissions policies in the search box type "lambdabasic"
g.- Checkmark the AWS managed policy **"AWSLambdaBasicExecutionRole"**
h.- Under Create policy clear the Search box 
i- Click Filter policies and checkmark "Customer managed"
j.- Scroll down and checkmark the Customer managed policy **"AssumeLinkedRolePolicy"**
k.-  Click "Next:Tags" button and click "Next: Review" button too
l.- Under Review, in Role name `*` type **AutoTaggingMasterLambda.** 
m.- In Role description type "Resource Role to give permission to lambda autotagging function in *receiver account* to assume roles named **"AutoTaggingExecuteLambda"** in linked account with AWS STS service". 
Observe that in Trusted entities you got AWS service: lambda.amazonaws.com and two policies attached to the role
n.- Click "Create Role Button"

![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/2.png)

Is noteworthy to say you should keep the same role name **"AutoTaggingExecuteLambda"** in every new linked accounts in your organization so as not to keep adding new policies into this role

# 3 Setting up a Role in Linked Account with the appropiate permsissions to execute Lambda functions to Tag Newly deployed resources
Create a role in *Linked Accoun*t that has enough permissions to execute lambda for the auto-tagging job. 
Follow the steps:
**Create a Policy **"AutoTaggingMasterLambdaPolicy"** to allow AutoTaggingMasterLambda role in receiver account  to assume any role named AWSLambdaBasicExecutionRole in any **Linked account **

a.- Be sure you are in *Linked Account* 222222222222
b.- At the console screen go to services and type in the text box `"IAM"` or under All
    ```Services > Security, Identity, & Compliance > IAM```
c.- In `Identity and Access Managment (IAM) menu > go to Policies` and click `"Create policy"` button
d.- Click Create policy next.
e.- In Create policy window select JSON tab. Click and paste the following policy and click the "Next: tags" button:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "sqs:UntagQueue",
                "logs:*",
                "iam:TagMFADevice",
                "codepipeline:ListTagsForResource",
                "cloudformation:UpdateStackSet",
                "cloudformation:CreateChangeSet",
                "iam:TagSAMLProvider",
                "codebuild:UpdateProject",
                "s3:DeleteJobTagging",
                "ssm:RemoveTagsFromResource",
                "cloudtrail:AddTags",
                "ssm:AddTagsToResource",
                "codepipeline:GetPipeline",
                "cloudformation:UpdateStack",
                "s3:PutObjectTagging",
                "s3:DeleteObjectTagging",
                "iam:UntagSAMLProvider",
                "s3:DeleteStorageLensConfigurationTagging",
                "ec2:CreateTags",
                "ssm:GetParameters",
                "s3:DeleteObjectVersionTagging",
                "iam:TagPolicy",
                "codepipeline:UntagResource",
                "cloudformation:UntagResource",
                "resource-explorer:*",
                "sns:TagResource",
                "mediastore:UntagResource",
                "cloudformation:UpdateStackInstances",
                "iam:UntagRole",
                "ec2:DeleteTags",
                "codepipeline:CreatePipeline",
                "iam:TagRole",
                "s3:ReplicateTags",
                "cloudformation:UpdateTerminationProtection",
                "codepipeline:CreateCustomActionType",
                "sns:UntagResource",
                "codepipeline:TagResource",
                "s3:PutBucketTagging",
                "tag:*",
                "codebuild:BatchGetProjects",
                "s3:PutStorageLensConfigurationTagging",
                "s3:PutObjectVersionTagging",
                "s3:PutJobTagging",
                "iam:UntagServerCertificate",
                "iam:TagUser",
                "iam:UntagUser",
                "sqs:TagQueue",
                "ssm:ListTagsForResource",
                "iam:UntagMFADevice",
                "iam:TagServerCertificate",
                "cloudformation:TagResource",
                "iam:UntagPolicy",
                "iam:UntagOpenIDConnectProvider",
                "iam:UntagInstanceProfile",
                "iam:TagOpenIDConnectProvider",
                "mediastore:TagResource",
                "codepipeline:PutWebhook",
                "cloudtrail:RemoveTags",
                "iam:TagInstanceProfile"
            ],
            "Resource": "*"
        }
    ]
}
```

h.- Click "Next: Review" button
i.- In Review policy window in Name type **"AutoTaggingExecuteLambdaPolicy"**
j.- In Description type "Policy to enable **AutoTaggingExecuteLambda** Role to tag newly deployed resources in this Account" and click "Create policy"

![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/3.png)

#### Create AutoTaggingExecuteLambda role in Linked account
a.- Be sure you are in *Receiver Account* 222222222222
b.- At the console screen go to services and type in the text box `"IAM"` or under All services > Security, Identity, & Compliance > IAM
d.- In Create Role window > Under "Select type of trusted entity" keep AWS service as your choice
 ```json
 {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111111111111:role/AutoTaggingMasterLambda"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```
e.- In "Choose a use case" select "Lambda" and click "Next: Permissions" button
![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/4.png)
f.- In next window, under Attach Permissions policies in the search box type "lambdabasic"
g.- Checkmark the AWS managed policy **"AWSLambdaBasicExecutionRole"**
h.- Under Create policy clear the Search box 
i- Click Filter policies and checkmark "Customer managed"
j.- Scroll down and checkmark the Customer managed policy **"AutoTaggingExecuteLambdaPolicy"**
k.-  Click "Next:Tags" button and click "Next: Review" button too
l.- Under Review, in Role name `*` type **AutoTaggingExecuteLambda.** 
m.- In Role description type "Resource Role to give permission to lambda autotagging function in *receiver account* to tag resources deployed in this account - Linked Account". 
Observe that in Trusted entities you got AWS service: lambda.amazonaws.com and two policies attached to the role.
n.- Click "Create Role Button"

![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/5.png)

Is noteworthy to say you should keep the same role name **"AutoTaggingExecuteLambda"** in every new linked accounts in your organization so as not to keep adding new policies into the Receiver Account

# 4. Deploy Autotagging Lambda Function in Receiver Account

We set our lambda function in virginia region or us-east-1. This is the endpoint for any deployment or creation event happening in any region in any account that is configured in the pipeline for **Auto-tagging* and in this lambda function. 

Create a **AutoTagging** lambda function with the console:

a.- First, be sure you are in Receiver Account in us-east-1 . In the console click the services tab and look for Lamdba under 
```
All services > Compute > Lambda or just type lambda in the text box. then hit Lambda
```
b.- In the AWS lambda window go to Functions.
c. Click the "Create function" buttom.
d. You will the following options to create your function Author from scratch, Use blueprint, Container Image, and Browse serverless app repository, choose Author from scratch.
e. In Function name type **"AutoTagging"** or any name you choose to, in Runtime look for Python 3.8
f.- In Permissions - click Change default execution role and select "Use an existing role". In the dialog box that opens up look for "AutoTaggingMasterLambda", this is the role we created in the previous step.
g.- Click "Create function" button
h.- Under Code source > In Environment click `lambda_function.py`
i.- Delete all existing code an replace it with the code provided in the `CreateTagCreatorID.py` file
j.- Once you paste the new code click "Deploy"
j.- In the Code Source menu click Test
k.- In Configure test event leave Create new test event selected, In event name type create_tags and click "Create Test" Button

![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/6.png)

# 5. Create SNS Topic 
Create a topic - **"SNStoAutoTaggingLambda"** and Subscribe it to Lambda Function **"AutoTagging"** *in ReceiverAccount*. So let us follow the next steps:

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

![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/7.png)

# 6. In `CloudWatch` in *Receiver Account* add the necessary permissions to `Event Buses` 
In Event Buses we have to manage event bus permissions to enabble passing event metadata:
a.- Be sure you are in us-east-1 region in *Receiver Account*
b.- At the console screen go to services and type in the text box `"Cloudwatch"` or under All
```
services > Management & Governance > Cloudwatch
```
c.- In `Event Buses` item in the menu go to `Event Buses`
d.- Under the permissions section click add permission. A "Add Permission" dialog box opens up. In the Type text box click the arrow and select Organization. In Organization ID select My Organization, your organization Id "my-org-id-1234" should be pre-populated. Hit the Add blue button.

![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/9.png)

A Resource-based policy for default event bus is automatically generated.
To check the policy go to ```Amazon EventBridge > Event buses > default``` and you check Permissions tab you will see a Resource-based policy like this
The default event bus name is something like this - `arn:aws:events:us-east-1:111111111111:event-bus/default`

![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/8.png)

And the resulting Reso policy would look something like this:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "this-is-how-i-pass-events-btwn-accounts-in-my-org",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "events:PutEvents",
    "Resource": "arn:aws:events:us-east-1:111111111111:event-bus/default",
    "Condition": {
      "StringEquals": {
        "aws:PrincipalOrgID": "my-organization-id"
      }
    }
  }]
}
```


# 7 In Receiver Account create an EventBridge Rule in us-east-1 -or Virginia Region and use as target SnsSendToLambda.
Create a rule that captures all creation events in `Sender Acccount` using `AWS API Call via CloudTrail` and select **SnsSendToLambda** as target:
a.- Be sure you are in `us-east-1` region in `Receiver Account` 
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
Notice that this is exactly the same rule we used in CloudWatch in Receiver Account

h.- In Select event bus leave it as it is, `"AWS default event bus"` and `"Enable the rule on the selected bus"`
i.- In Select` Targets > in Target click the text box, scroll up and select "SNS Topic"`
j.- In Topic text box select **"SnsSendToLambda"**
k.- Click `"Create Rule" `button. 

![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/9.png)

# 8  In *Linked Account* create a matching `EventBridge Rule` in same region (we are using us-east-1 - Virginia Region) and use as target the` event Bus `in matching us-east-1 region in *Receiver Account*.
Create a rule that captures all creation events in `Sender Acccount` using `AWS API Call via CloudTrail` and select default event bus as target:
a.- Be sure you are in us-east-1 region in `Sender Account` 
b.- At the console screen go to services and type in the text box `"EventBridge"` or under ``All services > Application Integration > Amazon EventBridge```

c.- In the ```Amazon EventBridge menu select Rules and click "Create Rule" button``
d.- Under Name and ```Description > Name type "EventAutoTaggingRule"``
e.- Add a Description "Rule to send creation events to default event bus in receiver account" if you choose to, it is optional
f.- In Define pattern choose ``"Event pattern" > Custom Pattern``
g.- Copy paste the following json pattern
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
Notice that this is exactly the same rule we used in CloudWatch in Receiver Account

h.- In Select event bus leave it as it is, ```"AWS default event bus" ```and "Enable the rule on the selected bus"

i.- In ``Select Targets > in Target click the text box, scroll up and select "Event bus in another AWS account"``
j.- In Event Bus text box type `"arn:aws:events:us-east-1:111111111111:event-bus/default"` (be sure to replace the Account number with your designated Receiver Account)
k.- Select "Create a new role for this specific resource". EventBridge will create a role for you with the right permissions to pass events into the event bus. Click configure details button.

l.- Click "Create Rule" button. 

![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/10.png)

# 9. Add the necessary permissions to Event Buses in CloudWatch in Linked Account
In `Event Buses` we have to manage event bus permissions to enabble passing event metadata:
a.- Be sure you are in us-east-1 region in *Sender Account*
b.- At the console screen go to services and type in the text box `"Cloudwatch"` or under ```All services > Management & Governance > Cloudwatch```
c.- In `Event Buses` item in the menu go to `Event Buses`.
d.- Under the permissions section click add permission. A `"Add Permission"` dialog box opens up. In the Type text box click the arrow and select Organization. In `Organization ID `select My Organization, your organization Id `"my-org-id-1234"` should be pre-populated. Hit the Add blue button.


A Resource-based policy for default event bus is automatically generated.
To check the policy go to ```Amazon EventBridge > Event buses > default ```and you check Permissions tab you will see a Resource-based policy like this
The default event bus name is something like this - `arn:aws:events:us-east-1:222222222222:event-bus/default`

And the resulting Reso policy would look something like this:
```json
{
  "Version": "2012-10-17",
  "Statement": [{. 
    "Sid": "this-is-how-i-pass-events-btwn-accounts-in-my-org",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "events:PutEvents",
    "Resource": "arn:aws:events:us-east-1:222222222222:event-bus/default",
    "Condition": {
      "StringEquals": {
        "aws:PrincipalOrgID": "my-organization-id"
      }
    }
  }]
}
```

# 10. Deploy a VPC in *Linked Account* and Check the Tags
Either by console or by AWS CLi SDK for boto3 deploy a Vpc or any resource that you desire.
Using the AWS Console:
a. In *Sender Account,* in us-east-1 go to the resource tab
b. In the services search text box type vpc or under "Networking & Content Delivery" look for VPC. Click VPC
c.- In the menu to the left click "Your VPCs"
d.- In Your VPCs window click "Create VPC" button
e.- In Create VPC > VPC settings > Name tag type test-project or any name you want to.
f.- In IPv4 CIDR block type 10.0.0.0/24, leave the rest of the settings as it is.
g.- Click the "Create VPC" button.
{pegar imagen aqui}
h.- You will be redirected to the newly created vpc window details. under the "Tags" tab click it and check for the tags. 

![alt text](https://raw.githubusercontent.com/SynergygraphicIB/Automatization-of-Tag-Creator-based-on-UserName-Across-Accounts/main/img/11.png)

You will see the Following tags; create_at, UserName, Name, and creatorId. 



### Note: To implement the function in different regions, repeat steps 4 to 8 and replace the region values as applicable
