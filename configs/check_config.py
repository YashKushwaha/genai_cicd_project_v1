from aws_scripts import (AMImanager,
           IAMmanager, KeyPairManager, SecurityGroupManager,
            SubnetManager, VpcManager, ECRManager, EC2Manager)

import configparser
import os
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

instance_exists = ec2_manager.find_instance_by_name(ec2_name)

print('instance_exists -> ', instance_exists)


sys.exit('Done')

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
if not repo_exists:
    sys.exit(f'No ECR repo with name -> {repo_name}')
############################################
iam_manager = IAMmanager(session.client('iam'))
profile_name = dict(config.items('iam')).get('instance_profile')
print(profile_name)
role_exists = iam_manager.role_exists(profile_name)
if not role_exists:
    sys.exit(f"Specified IAM role doesn't exist -> {profile_name}")
############################################