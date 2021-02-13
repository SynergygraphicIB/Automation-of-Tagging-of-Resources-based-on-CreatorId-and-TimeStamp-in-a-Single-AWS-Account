# Automation-of-Tagging-of-Resources-base-on-Creator-Id

A Lambda function to create tags with the creators ID to track who made what. The lambda function is triggered when any AWS resource is deployed either by console or by AWS SDK for Python (Boto3). Once the resource of resources are deployed cloudwatch send the event to Lambda wherein it launches CreateTagCreatorID, function which creates a Key Tag/value With the user who is deploying the resource.

