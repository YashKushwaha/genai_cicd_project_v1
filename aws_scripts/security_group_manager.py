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

    def get_ingress_rule_on_port(self, port, cidr="0.0.0.0/0", protocol="tcp", description=None):
        return [{
            "IpProtocol": protocol,
            "FromPort": port,
            "ToPort": port,
            "IpRanges": [{"CidrIp": cidr, 
                          "Description": description or f"Port {port}"
           }]
        }]
    
    def add_ingress_rule_to_group(self, sg_id, ingress_rule):
        response = self.ec2_client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=ingress_rule
            )
        return response
    
    def add_ingress_rules_from_dict_to_group(self, sg_id, ports_mapping):
        existing_ports = self.get_existing_ingress_ports(sg_id)
        rules = []
        for name, port in ports_mapping.items():
            if port in existing_ports:
                continue
            rule = self.get_ingress_rule_on_port(int(port), description = name)
            rules.extend(rule)
        if rules:
            response = self.ec2_client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=rules
            )
        else:
            response=True
        return response
        
    def get_security_group_rules(self, group_id):
        response = self.ec2_client.describe_security_groups(GroupIds=[group_id])
        sg = response['SecurityGroups'][0]

        ingress_rules = sg.get('IpPermissions', [])
        egress_rules = sg.get('IpPermissionsEgress', [])
        return ingress_rules, egress_rules

    def get_existing_ingress_ports(self, group_id):
        ingress_rules, _ = self.get_security_group_rules(group_id)
        ports = [i.get('FromPort') for i in ingress_rules]
        return ports
