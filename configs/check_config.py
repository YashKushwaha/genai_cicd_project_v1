import os

print(os.getcwd())
print(os.listdir())

from aws_scripts import (AMImanager,
           IAMmanager, KeyPairManager, SecurityGroupManager,
            SubnetManager, VpcManager, ECRManager, EC2Manager)

import configparser

import boto3
import sys
import json

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

config = configparser.ConfigParser()
config.read('configs/infra_config.ini')

session = boto3.session.Session()
ec2_client = session.client('ec2')

ec2_manager = EC2Manager(ec2_client)
ec2_name = dict(config.items('ec2')).get('instance_name')

instance = ec2_manager.find_instance_by_name(ec2_name)

instance_id = instance['InstanceId'] if instance else None
instance_name=dict(config.items('ec2')).get('instance_name')
instance_type=dict(config.items('ec2')).get('instance_type')
###################################
vpc_manager = VpcManager(ec2_client)
vpc_name = dict(config.items('vpc')).get('name')
vpc_id = vpc_manager.find_vpc_by_name(vpc_name)

if vpc_id is None:
    sys.exit(f'No vpc found with the name -> {vpc_name}')
###################################
subnet_manager = SubnetManager(ec2_client)
subnet_name = dict(config.items('subnet')).get('name')

subnet_id = subnet_manager.find_subnet_by_name(subnet_name,vpc_id=vpc_id )

if subnet_id is None:
    sys.exit(f'No subnet found with the name -> {vpc_name} in the vpc {vpc_name}')
###################################
ami_manager = AMImanager(ec2_client)
ami_id = dict(config.items('ami')).get('ami_id')
if ami_id is None:
    ami_id = ami_manager.get_free_tier_aws_ami()

if not ami_manager.validate_ami(ami_id):
    sys.exit(f'No ami found with the id -> {ami_id}')

###################################
sg_manager = SecurityGroupManager(ec2_client)
security_group_name = dict(config.items('security_group')).get('security_group_name')
sg_id = sg_manager.find_security_group(security_group_name, vpc_id=vpc_id)
if (sg_id is None): 
    if(dict(config.items('security_group')).get('create_new', False)):
        description = 'Security group for Project'
        sg_id = sg_manager.create_security_group(security_group_name, description, vpc_id=vpc_id)
    else:
        sys.exit(f'No security group found with the name -> {security_group_name} in vpc -> {vpc_id}')

ingress_rules = dict(config.items('security_group')).get('ports', {})
ingress_rules = json.loads(ingress_rules)
sg_manager.add_ingress_rules_from_dict_to_group(sg_id, ingress_rules)
###################################
key_pair_manager = KeyPairManager(ec2_client)
key_name = dict(config.items('key-pair')).get('name')
key_exists = key_pair_manager.key_pair_exists(key_name)
if not key_exists:
    sys.exit(f'No key found with the name -> {key_name}')


############################################
ecr_manager = ECRManager(ecr_client = session.client('ecr'))
repo_name = dict(config.items('ecr')).get('repo_name')
repo_exists = ecr_manager.repo_exists(repo_name)
print('repo_exists -> ', repo_exists)

if (not repo_exists) and not dict(config.items('ecr')).get('create_new'):
    sys.exit(f'No ECR repo with name -> {repo_name}')
############################################
iam_manager = IAMmanager(session.client('iam'))
profile_name = dict(config.items('iam')).get('instance_profile')
print(profile_name)
role_exists = iam_manager.role_exists(profile_name)
if not role_exists:
    sys.exit(f"Specified IAM role doesn't exist -> {profile_name}")

iam_instance_profile = iam_manager.find_instance_profile_for_role(profile_name)
############################################

result = dict(vpc_id=vpc_id, subnet_id=subnet_id, ami_id=ami_id,
                security_group_ids = [sg_id],
                key_name=key_name, iam_instance_profile=iam_instance_profile, 
                repo_name=repo_name, instance_name=instance_name, instance_type=instance_type)

with open(os.environ.get('GITHUB_OUTPUT', 'GITHUB_OUTPUT.txt'), 'a') as env_file:
    if instance_id is not None:
        env_file.write("ec2_import_required=true\n")
        env_file.write(f"instance_id={instance_id}\n")
        #env_file.write(f"iam_instance_profile={iam_instance_profile}\n")
    if repo_exists:
        env_file.write("ecr_import_required=true\n")
        env_file.write(f"repo_name={repo_name}\n")
# Write to GitHub environment file
github_env = os.environ.get('GITHUB_ENV', 'GITHUB_ENV.txt')
print('github_env -> ', github_env)

with open(github_env, 'a') as env_file:
    for i, j in result.items():
        key = f'TF_VAR_{i}'
        if isinstance(j, list):
            value = json.dumps(j)  # ensures JSON-compatible string: ["value"]
        else:
            value = str(j)
        env_file.write(f"{key}={value}\n")

print(f"Wrote to {github_env}:")
with open(github_env) as f:
    print(f.read())