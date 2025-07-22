import ipaddress
from .vpc_manager import VpcManager

class SubnetManager:
    def __init__(self, ec2_client):
        self.ec2_client = ec2_client
        self.vpc_manager = VpcManager(self.ec2_client)

    def cidr_within(self, subnet_cidr, vpc_cidr):
        return ipaddress.IPv4Network(subnet_cidr).subnet_of(ipaddress.IPv4Network(vpc_cidr))

    def find_subnet_by_name(self, name, vpc_id=None):
        filters = [{"Name": "tag:Name", "Values": [name]}]
        if vpc_id:
            filters.append({"Name": "vpc-id", "Values": [vpc_id]})
        response = self.ec2_client.describe_subnets(Filters=filters)
        if response["Subnets"]:
            return response["Subnets"][0]['SubnetId']
        return None

    def _generate_available_subnet_cidr(self, vpc_cidr, used_cidrs, new_prefix=24):
        vpc_network = ipaddress.IPv4Network(vpc_cidr)
        existing_networks = [ipaddress.IPv4Network(cidr) for cidr in used_cidrs]

        for subnet in vpc_network.subnets(new_prefix=new_prefix):
            if all(not subnet.overlaps(existing) for existing in existing_networks):
                return str(subnet)

        raise Exception(f"No available /{new_prefix} subnet in VPC {vpc_cidr}")

    def get_or_create_subnet(self, subnet_name, subnet_cidr=None, vpc_name_or_id=None, az=None, map_public_ip=True):
        # Step 1: Resolve VPC ID
        if not vpc_name_or_id:
            raise ValueError("You must provide a VPC ID or Name.")

        vpc_id = vpc_name_or_id if vpc_name_or_id.startswith("vpc-") else self.vpc_manager.find_vpc_by_name(vpc_name_or_id)
        if not vpc_id:
            raise Exception(f"VPC '{vpc_name_or_id}' does not exist.")

        # Step 2: Check by name first
        existing_by_name = self.find_subnet_by_name(subnet_name, vpc_id=vpc_id)
        if existing_by_name:
            print(f"Subnet already exists with name '{subnet_name}'")
            return existing_by_name["SubnetId"]

        # Step 3: Describe VPC
        vpc = self.ec2_client.describe_vpcs(VpcIds=[vpc_id])["Vpcs"][0]
        vpc_cidr = vpc["CidrBlock"]

        # Step 4: Generate CIDR if not provided
        if subnet_cidr is None:
            existing_subnets = self.ec2_client.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
            used_cidrs = [s["CidrBlock"] for s in existing_subnets["Subnets"]]
            subnet_cidr = self._generate_available_subnet_cidr(vpc_cidr, used_cidrs)
            print(f"Auto-generated CIDR: {subnet_cidr}")

        # Step 5: Validate CIDR
        if not self.cidr_within(subnet_cidr, vpc_cidr):
            raise ValueError(f"Subnet CIDR {subnet_cidr} is not within VPC CIDR {vpc_cidr}")

        # Step 6: Check if same CIDR already exists (even with different name)
        existing = self.ec2_client.describe_subnets(
            Filters=[
                {"Name": "vpc-id", "Values": [vpc_id]},
                {"Name": "cidr-block", "Values": [subnet_cidr]}
            ]
        )
        if existing["Subnets"]:
            print(f"Subnet already exists with CIDR {subnet_cidr}")
            return existing["Subnets"][0]["SubnetId"]

        # Step 7: Create the subnet
        params = {"VpcId": vpc_id, "CidrBlock": subnet_cidr}
        if az:
            params["AvailabilityZone"] = az
        subnet = self.ec2_client.create_subnet(**params)["Subnet"]

        if map_public_ip:
            self.ec2_client.modify_subnet_attribute(
                SubnetId=subnet["SubnetId"],
                MapPublicIpOnLaunch={"Value": True}
            )

        self.ec2_client.create_tags(
            Resources=[subnet["SubnetId"]],
            Tags=[{"Key": "Name", "Value": subnet_name}]
        )

        return subnet["SubnetId"]
