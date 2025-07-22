provider "aws" {
  region = var.region
}

resource "aws_instance" "web" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  subnet_id              = var.subnet_id
  vpc_security_group_ids = var.security_group_ids
  associate_public_ip_address = true

  user_data = <<-EOF
                #!/bin/bash
                usermod -aG docker ec2-user
                shutdown -h now
                EOF

  tags = {
    Name = var.instance_name
  }
}

resource "aws_ecr_repository" "genai_repo" {
  name = var.repo_name

  image_scanning_configuration {
    scan_on_push = true
  }

  image_tag_mutability = "MUTABLE"

  tags = {
    Name        = var.repo_name

  }
}
