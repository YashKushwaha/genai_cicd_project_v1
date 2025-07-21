import boto3

class SecurityGroupManager:
    def __init__(self, ec2_client):
        self.ec2_client = ec2_client

    def find_security_group(self, name, vpc_id):
        response = self.ec2_client.describe_security_groups(
            Filters=[
                {"Name": "group-name", "Values": [name]},
                {"Name": "vpc-id", "Values": [vpc_id]}
            ]
        )
        if response["SecurityGroups"]:
            return response["SecurityGroups"][0]["GroupId"]
        return None

    def create_security_group(self, name, description, vpc_id, ingress_rules=None, egress_rules=None, tags=None):
        response = self.ec2_client.create_security_group(
            GroupName=name,
            Description=description,
            VpcId=vpc_id
        )
        sg_id = response["GroupId"]

        if ingress_rules:
            self.ec2_client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=ingress_rules
            )

        if egress_rules:
            self.ec2_client.authorize_security_group_egress(
                GroupId=sg_id,
                IpPermissions=egress_rules
            )

        if tags:
            self.ec2_client.create_tags(Resources=[sg_id], Tags=tags)

        return sg_id

    def get_or_create(self, name, description, vpc_id, ingress_rules=None, egress_rules=None, tags=None):
        sg_id = self.find_security_group(name, vpc_id)
        if sg_id:
            print(f"Found existing security group: {sg_id}")
            return sg_id

        print(f"Creating security group: {name}")
        return self.create_security_group(
            name=name,
            description=description,
            vpc_id=vpc_id,
            ingress_rules=ingress_rules,
            egress_rules=egress_rules,
            tags=tags
        )

    def get_ingress_rule_on_port(self, port, cidr="0.0.0.0/0", protocol="tcp"):
        return [{
            "IpProtocol": protocol,
            "FromPort": port,
            "ToPort": port,
            "IpRanges": [{"CidrIp": cidr}]
        }]
    
    def add_ingress_rule_to_group(self, sg_id, ingress_rule):
        response = self.ec2_client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=ingress_rule
            )
        return response