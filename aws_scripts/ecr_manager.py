import boto3
from botocore.exceptions import ClientError

class ECRManager:
    def __init__(self, ecr_client=None):
        self.ecr = ecr_client or boto3.client('ecr')

    def repo_exists(self, repo_name):
        try:
            self.ecr.describe_repositories(repositoryNames=[repo_name])
            return True
        except self.ecr.exceptions.RepositoryNotFoundException:
            return False

    def create_repo(self, repo_name, tags=None, scan_on_push=True):
        try:
            response = self.ecr.create_repository(
                repositoryName=repo_name,
                imageScanningConfiguration={
                    'scanOnPush': scan_on_push
                },
                tags=tags or []
            )
            print(f"ECR repository created: {repo_name}")
            return response['repository']
        except ClientError as e:
            print(f"Error creating repository: {e}")
            return None

    def get_or_create_repo(self, repo_name, tags=None):
        if self.repo_exists(repo_name):
            print(f"ECR repository already exists: {repo_name}")
            return self.ecr.describe_repositories(repositoryNames=[repo_name])['repositories'][0]
        return self.create_repo(repo_name, tags=tags)

    def delete_repo(self, repo_name, force=False):
        try:
            self.ecr.delete_repository(repositoryName=repo_name, force=force)
            print(f"ECR repository deleted: {repo_name}")
        except self.ecr.exceptions.RepositoryNotFoundException:
            print(f"Repository not found: {repo_name}")

