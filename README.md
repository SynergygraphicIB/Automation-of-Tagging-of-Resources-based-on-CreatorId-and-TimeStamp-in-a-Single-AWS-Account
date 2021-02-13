# Automation-of-Tagging-of-Resources-base-on-Creator-Id

A Lambda function to create tags with the creators ID to track who made what. The lambda function is triggered when any AWS resource is deployed either by console or by AWS SDK for Python (Boto3). Once the resource of resources are deployed cloudwatch send the event to Lambda wherein it launches CreateTagCreatorID, function which creates a Key Tag/value With the user who is deploying the resource.

# Crear funcion Lambda
Crear funcion lambda con roles de administrador para que pueda capturar todos los eventos y cargar la funcion lambda.py 

# Crear  event Rule en cloud Watch
En cloud watch crear una regla con el evento CloudWatchEvent.json, esta regla asiganarla  a la funcion lambda creada anteriormente. 
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
