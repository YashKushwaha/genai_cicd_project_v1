import boto3

class EC2Manager:
    def __init__(self, ec2_client=None):
        self.ec2 = ec2_client or boto3.client('ec2')

    def find_instance_by_name(self, name):
        response = self.ec2.describe_instances(
            Filters=[
                {"Name": "tag:Name", "Values": [name]},
                {"Name": "instance-state-name", "Values": ["pending", "running", "stopped"]}
            ]
        )
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                return instance  # Return the first matched instance
        return None

    def create_instance(self, name, ami_id, instance_type, key_name, subnet_id, security_group_ids, instance_profile_arn=None):
        print(f"Creating EC2 instance '{name}'...")
        instance_params = {
            "ImageId": ami_id,
            "InstanceType": instance_type,
            "KeyName": key_name,
            "SubnetId": subnet_id,
            "SecurityGroupIds": security_group_ids,
            "MinCount": 1,
            "MaxCount": 1,
            "TagSpecifications": [{
                "ResourceType": "instance",
                "Tags": [{"Key": "Name", "Value": name}]
            }]
        }

        if instance_profile_arn:
            instance_params["IamInstanceProfile"] = {"Arn": instance_profile_arn}

        response = self.ec2.run_instances(**instance_params)
        return response['Instances'][0]

    def get_or_create_instance(self, name, **kwargs):
        existing = self.find_instance_by_name(name)
        if existing:
            print(f"Found existing instance: {existing['InstanceId']}")
            return existing
        return self.create_instance(name, **kwargs)
