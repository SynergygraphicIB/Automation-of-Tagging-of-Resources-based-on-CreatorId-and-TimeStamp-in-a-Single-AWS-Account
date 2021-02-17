import json
import boto3
from datetime import datetime

s3 = boto3.resource('s3')
ec2 = boto3.resource('ec2')


def lambda_handler(event, context):
       
    event= event.get("responsePayload")
    
    eventName=event["detail"].get("eventName")
    principaID= event["detail"]["userIdentity"].get("arn")
    region=event["detail"].get("awsRegion")

    client = boto3.client('ec2', region_name = region)
    
    if(eventName == "CreateSubnet"):
        subnetID= event["detail"]["responseElements"]["subnet"].get("subnetId")
        addTagClient(client,principaID,subnetID)
        
    elif(eventName == "CreateSecurityGroup"):
        groupId= event["detail"]["responseElements"].get("groupId")
        addTagClient(client,principaID,groupId)
        
    elif(eventName == "CreateVpc"):
        vpcId=event["detail"]["responseElements"]["vpc"].get("vpcId")
        addTagClient(client,principaID,vpcId)
        
    elif(eventName == "CreateRouteTable"):
        routeTableId=event["detail"]["responseElements"]["routeTable"].get("routeTableId")
        addTagClient(client,principaID,routeTableId)

    elif(eventName == "CreateInternetGateway"):
        igwId=event["detail"]["responseElements"]["internetGateway"].get("internetGatewayId")
        addTagClient(client,principaID,igwId)

    elif(eventName == "CreateNetworkAcl"):
        naclId=event["detail"]["responseElements"]["networkAcl"].get("networkAclId")
        addTagClient(client,principaID,naclId)

    elif(eventName == "CreateNetworkInterface"):
        naclId=event["detail"]["responseElements"]["networkInterface"].get("networkInterfaceId")
        addTagClient(client,principaID,naclId)

    elif(eventName == "CreateSnapshot"):
        snapshoID=event["detail"]["responseElements"].get("snapshotId")
        addTagSnapshot(principaID, snapshoID)

    elif(eventName == "CreateVolume"):
        volumeId=event["detail"]["responseElements"].get("volumeId")
        addTagClient(client,principaID,volumeId)
        
    elif(eventName == "RunInstances"):
        instanceId=event["detail"]["responseElements"]["instancesSet"]["items"][0].get("instanceId")
        addTagClient(client,principaID,instanceId)

    elif(eventName == "CreateImage"):
        instanceId=event["detail"]["responseElements"].get("imageId")
        addTagClient(client,principaID,instanceId)
    
    elif(eventName == "CreateTransitGateway"):
        idTgw=instanceId=event["detail"]["responseElements"]["CreateTransitGatewayResponse"]["transitGateway"].get("transitGatewayId")
        addTagClient(client,principaID, idTgw)

    elif(eventName == "CreateTransitGatewayVpcAttachment"):
        idTgwA=instanceId=event["detail"]["responseElements"]["CreateTransitGatewayVpcAttachmentResponse"]["transitGatewayVpcAttachment"].get("transitGatewayAttachmentId")
        addTagClient(client,principaID, idTgwA)
    
    elif(eventName == "AllocateAddress"):
        allocateid=instanceId=event["detail"]["responseElements"].get("allocationId")
        addTagClient(client,principaID, allocateid)
    
    elif(eventName == "CreateNatGateway"):
        natgwId=event["detail"]["responseElements"]["CreateNatGatewayResponse"]["natGateway"].get("natGatewayId")
        addTagClient(client,principaID, natgwId)
    


#ClientTags
def addTagClient(client,principaID, ids):
    response = client.create_tags(
        Resources=[
            ids,
        ],
        Tags=[
            {
                'Key': 'creatorID',
                'Value': principaID,
            },
        ],
    )
