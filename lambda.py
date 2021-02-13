import json
import boto3
from datetime import datetime

s3 = boto3.resource('s3')
ec2 = boto3.resource('ec2')
client= boto3.client('ec2')


def lambda_handler(event, context):
    eventName=event["detail"].get("eventName")
    principaID= event["detail"]["userIdentity"].get("arn")
    
    content= json.dumps(event, indent=4, sort_keys=True)
    now = datetime.now()
    namefile="CreateTagCreatorIdEvent-"+str(now)+".txt"
    s3.Object('lambda-event-test-jesus', namefile).put(Body=content)
    
    
    if(eventName == "CreateSubnet"):
        subnetID= event["detail"]["responseElements"]["subnet"].get("subnetId")
        addTagSubnet(principaID,subnetID)
        
    elif(eventName == "CreateSecurityGroup"):
        groupId= event["detail"]["responseElements"].get("groupId")
        addTagSecurityGroup(principaID,groupId)
        
    elif(eventName == "CreateVpc"):
        vpcId=event["detail"]["responseElements"]["vpc"].get("vpcId")
        addTagClient(principaID,vpcId)
        
    elif(eventName == "CreateRouteTable"):
        routeTableId=event["detail"]["responseElements"]["routeTable"].get("routeTableId")
        addTagRoutetable(principaID,routeTableId)

    elif(eventName == "CreateInternetGateway"):
        igwId=event["detail"]["responseElements"]["internetGateway"].get("internetGatewayId")
        addTagInternetGateway(principaID,igwId)

    elif(eventName == "CreateNetworkAcl"):
        naclId=event["detail"]["responseElements"]["networkAcl"].get("networkAclId")
        addTagNetworkAlc(principaID,naclId)

    elif(eventName == "CreateNetworkInterface"):
        naclId=event["detail"]["responseElements"]["networkInterface"].get("networkInterfaceId")
        addTagNetworkAlc(principaID,naclId)

    elif(eventName == "CreateSnapshot"):
        snapshoID=event["detail"]["responseElements"].get("snapshotId")
        addTagSnapshot(principaID, snapshoID)

    elif(eventName == "CreateVolume"):
        volumeId=event["detail"]["responseElements"].get("volumeId")
        addTagVolume(principaID,volumeId)
        
    elif(eventName == "RunInstances"):
        instanceId=event["detail"]["responseElements"]["instancesSet"]["items"][0].get("instanceId")
        addTagInstance(principaID,instanceId)

    elif(eventName == "CreateImage"):
        instanceId=event["detail"]["responseElements"].get("imageId")
        addTagInstance(principaID,instanceId)
    
    elif(eventName == "CreateTransitGateway"):
        idTgw=instanceId=event["detail"]["responseElements"]["CreateTransitGatewayResponse"]["transitGateway"].get("transitGatewayId")
        addTagClient(principaID, idTgw)

    elif(eventName == "CreateTransitGatewayVpcAttachment"):
        idTgwA=instanceId=event["detail"]["responseElements"]["CreateTransitGatewayVpcAttachmentResponse"]["transitGatewayVpcAttachment"].get("transitGatewayAttachmentId")
        addTagClient(principaID, idTgwA)
    
    elif(eventName == "AllocateAddress"):
        allocateid=instanceId=event["detail"]["responseElements"].get("allocationId")
        addTagClient(principaID, allocateid)
    
    elif(eventName == "CreateNatGateway"):
        natgwId=event["detail"]["responseElements"]["CreateNatGatewayResponse"]["natGateway"].get("natGatewayId")
        addTagClient(principaID, natgwId)



#Subnet        
def addTagSubnet(principaID,subnetID):
    subnet = ec2.Subnet(subnetID)
    subnet.create_tags(Tags=[{"Key": "creatorID", "Value": principaID}])

#SecurityGroup    
def addTagSecurityGroup(principaID,groupId):
    security_group = ec2.SecurityGroup(groupId)
    security_group.create_tags(Tags=[{"Key": "creatorID", "Value": principaID}])

#ImageID
def addTagImage(principaID,imageId):
    image = ec2.Image(imageId)
    image.create_tags(Tags=[{"Key": "creatorID", "Value": principaID}])

#Instance
def addTagInstance(principaID,instanceId):
    instance = ec2.Instance(instanceId)
    instance.create_tags(Tags=[{"Key": "creatorID", "Value": principaID}])
    
#InternetGateway
def addTagInternetGateway(principaID,igwId):
    internet_gateway = ec2.InternetGateway(igwId)
    internet_gateway.create_tags(Tags=[{"Key": "creatorID", "Value": principaID}])
    
#NetworkAcl 
def addTagNetworkAlc(principaID,naclId):
    network_acl = ec2.NetworkAcl(naclId)
    network_acl.create_tags(Tags=[{"Key": "creatorID", "Value": principaID}])
    
#NetworkInterface
def addTagNetworkInterface(principaID,networkInterfaceId):
    network_interface = ec2.NetworkInterface(networkInterfaceId)
    network_interface.create_tags(Tags=[{"Key": "creatorID", "Value": principaID}])

#RouteTable
def addTagRoutetable(principaID,routeTableId):
    route_table = ec2.RouteTable(routeTableId)
    route_table.create_tags(Tags=[{"Key": "creatorID", "Value": principaID}])
    
#Snapshot
def addTagSnapshot(principaID, snapshoID):
    snapshot = ec2.Snapshot(snapshoID)
    snapshot.create_tags(Tags=[{"Key": "creatorID", "Value": principaID}])
    
#Volume    
def addTagVolume(principaID,volumeId):
    volume = ec2.Volume(volumeId)
    volume.create_tags(Tags=[{"Key": "creatorID", "Value": principaID}])

#VPC
def addTagVPC(principaID,vpcId):
    vpc = ec2.Vpc(vpcId)
    vpc.create_tags(Tags=[{"Key": "creatorID", "Value": principaID}])

#ClientTags
def addTagClient(principaID, ids):
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
