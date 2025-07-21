import boto3

class VpcManager:
    def __init__(self, ec2_client):
        self.ec2_client = ec2_client

    def get_cidr_block(self):
        return '10.0.0.0/16'

    def get_default_vpc(self):
        filters = [{"Name": 'isDefault', "Values": ["true"]}]
        vpcs = self.ec2_client.describe_vpcs(Filters=filters)
        if vpcs["Vpcs"]:
            return vpcs["Vpcs"][0]["VpcId"]
        else:
            return None

    def find_vpc_by_name(self, vpc_name):
        filters = [{"Name": "tag:Name", "Values": [vpc_name]}]
        vpcs = self.ec2_client.describe_vpcs(Filters=filters)
        if vpcs["Vpcs"]:
            return vpcs["Vpcs"][0]["VpcId"]
        else:
            return None

    def get_or_create_vpc(self, vpc_name=None, cidr_block=None):
        if vpc_name is None:
            return self.get_default_vpc()

        vpc_id = self.find_vpc_by_name(vpc_name)
        if vpc_id:
            return vpc_id

        if cidr_block is None:
            cidr_block = self.get_cidr_block()

        # Double-check CIDR not already in use
        existing_vpcs = self.ec2_client.describe_vpcs(Filters=[{
            "Name": "cidr-block", "Values": [cidr_block]
        }])
        if existing_vpcs["Vpcs"]:
            return existing_vpcs["Vpcs"][0]["VpcId"]

        # Create the VPC
        vpc = self.ec2_client.create_vpc(CidrBlock=cidr_block)
        vpc_id = vpc["Vpc"]["VpcId"]

        # Optional: wait (only with resource object) or manually poll for status if needed

        self.ec2_client.create_tags(Resources=[vpc_id], Tags=[
            {"Key": "Name", "Value": vpc_name}
        ])
        self.ec2_client.modify_vpc_attribute(
            VpcId=vpc_id, EnableDnsSupport={"Value": True}
        )
        self.ec2_client.modify_vpc_attribute(
            VpcId=vpc_id, EnableDnsHostnames={"Value": True}
        )

        return vpc_id
