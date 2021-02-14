# Automation-of-Tagging-of-Resources-base-on-Creator-Id

A Lambda function to create tags with the creators ID to track who made what. The lambda function is triggered when any AWS resource is deployed either by console or by AWS SDK for Python (Boto3). Once the resource of resources are deployed cloudwatch send the event to Lambda wherein it launches CreateTagCreatorID, function which creates a Key Tag/value With the user who is deploying the resource.

# Ceate funcion Lambda
First we create a Role with sufficient permissions to deploy AWS reources to attach to the lambda function use to create tags.
Then we create a function to create tags to the resource deployed either by AWS console or by SDK Boto3 for python

# Create event Rule en cloud Watch
En cloud watch we set a rule named CloudWatchEvent.json. Once this rule is triggered by the following events we launch our tag creation Lambda function to add the tag with the ID of the user who deployed the Resource.
      "CreateImage",
      "CreateInternetGateway",
      "CreateNatGateway",
      "CreateNetworkAcl",
      "CreateNetworkInterface",
      "CreateRouteTable",
      "CreateSecurityGroup",
      "CreateSnapshot",
      "CreateSubnet",
      "CreateVolume",
      "RunInstances",
      "CreateTransitGateway",
      "CreateTransitGatewayVpcAttachment",
      "AllocateAddress",
      "CreateVpc"
