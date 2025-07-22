import boto3
import os

class KeyPairManager:
    def __init__(self, ec2_client):
        self.ec2 = ec2_client

    def key_pair_exists(self, key_name):
        try:
            self.ec2.describe_key_pairs(KeyNames=[key_name])
            return True
        except self.ec2.exceptions.ClientError as e:
            if "InvalidKeyPair.NotFound" in str(e):
                return False
            raise

    def create_key_pair(self, key_name, save_path="."):
        if self.key_pair_exists(key_name):
            print(f"Key pair '{key_name}' already exists.")
            return

        print(f"Creating key pair: {key_name}")
        resp = self.ec2.create_key_pair(KeyName=key_name)
        key_material = resp['KeyMaterial']
        filepath = os.path.join(save_path, f"{key_name}.pem")

        with open(filepath, "w") as f:
            f.write(key_material)
        os.chmod(filepath, 0o400)
        print(f"Saved private key to {filepath}")

    def delete_key_pair(self, key_name, remove_local_file=True, local_path="."):
        if not self.key_pair_exists(key_name):
            print(f"Key pair '{key_name}' does not exist.")
            return

        print(f"Deleting key pair: {key_name}")
        self.ec2.delete_key_pair(KeyName=key_name)

        if remove_local_file:
            filepath = os.path.join(local_path, f"{key_name}.pem")
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Deleted local key file: {filepath}")
            else:
                print(f"No local key file found to delete: {filepath}")