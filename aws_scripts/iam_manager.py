import json
import botocore.exceptions
import boto3


class IAMmanager:
    def __init__(self, iam_client):
        self.iam_client = iam_client

    def role_exists(self, role_name):
        try:
            self.iam_client.get_role(RoleName=role_name)
            return True
        except self.iam_client.exceptions.NoSuchEntityException:
            return False

    def create_role_for_ec2(self, role_name, description="EC2 access role"):
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        print(f"Creating IAM Role '{role_name}'...")
        self.iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=description
        )

    def attach_managed_policy(self, role_name, policy_arn):
        attached = self.iam_client.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]
        if not any(p["PolicyArn"] == policy_arn for p in attached):
            print(f"Attaching policy '{policy_arn}' to role '{role_name}'...")
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )

    def attach_bedrock_inline_policy(self, role_name):
        policy_name = "BedrockAccessPolicy"
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream",
                        "bedrock:ListFoundationModels"
                    ],
                    "Resource": "*"
                }
            ]
        }

        print(f"Attaching inline Bedrock access policy to role '{role_name}'...")
        self.iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )

    def instance_profile_exists(self, profile_name):
        try:
            self.iam_client.get_instance_profile(InstanceProfileName=profile_name)
            return True
        except self.iam_client.exceptions.NoSuchEntityException:
            return False

    def create_instance_profile(self, profile_name):
        print(f"Creating Instance Profile '{profile_name}'...")
        self.iam_client.create_instance_profile(InstanceProfileName=profile_name)

    def add_role_to_instance_profile(self, role_name, profile_name):
        profile = self.iam_client.get_instance_profile(InstanceProfileName=profile_name)
        roles = [r["RoleName"] for r in profile["InstanceProfile"]["Roles"]]
        if role_name not in roles:
            print(f"Adding role '{role_name}' to profile '{profile_name}'...")
            self.iam_client.add_role_to_instance_profile(
                InstanceProfileName=profile_name,
                RoleName=role_name
            )

    def get_or_create_ecr_instance_profile(self, role_name="ec2_ecr_access_role", profile_name="ec2_ecr_access_profile"):
        if not self.role_exists(role_name):
            self.create_role_for_ec2(role_name)

        self.attach_managed_policy(
            role_name,
            "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
        )

        if not self.instance_profile_exists(profile_name):
            self.create_instance_profile(profile_name)

        self.add_role_to_instance_profile(role_name, profile_name)

        return profile_name

    def get_or_create_bedrock_instance_profile(self, role_name="ec2_bedrock_access_role", profile_name="ec2_bedrock_access_profile"):
        if not self.role_exists(role_name):
            self.create_role_for_ec2(role_name)

        self.attach_bedrock_inline_policy(role_name)

        if not self.instance_profile_exists(profile_name):
            self.create_instance_profile(profile_name)

        self.add_role_to_instance_profile(role_name, profile_name)

        return profile_name

    def get_or_create_custom_project_role(self, role_name="ec2_project_role", profile_name="ec2_project_profile"):
        if not self.role_exists(role_name):
            self.create_role_for_ec2(role_name)

        # Attach managed ECR policy
        self.attach_managed_policy(
            role_name,
            "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
        )

        # Attach Bedrock inline policy
        self.attach_bedrock_inline_policy(role_name)

        if not self.instance_profile_exists(profile_name):
            self.create_instance_profile(profile_name)

        self.add_role_to_instance_profile(role_name, profile_name)

        return profile_name


if __name__ == '__main__':
    iam_client = boto3.client("iam")
    iam_mgr = IAMmanager(iam_client)

    unified_profile = iam_mgr.get_or_create_custom_project_role()
    print(f"Use unified instance profile: {unified_profile}")
