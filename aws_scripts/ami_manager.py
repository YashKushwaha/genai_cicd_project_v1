def get_free_tier_aws_ami():
    return "ami-050fd9796aa387c0d"

def validate_ami(ec2_client, ami_id):
    try:
        response = ec2_client.describe_images(ImageIds=[ami_id])
        if response["Images"]:
            image = response["Images"][0]
            print(f"AMI found: {image['ImageId']} - {image['Name']} ({image['CreationDate']})")
            return True
        else:
            print(f"No AMI found for ID: {ami_id}")
            return False
    except ec2_client.exceptions.ClientError as e:
        print(f"Error: {e}")
        return False
