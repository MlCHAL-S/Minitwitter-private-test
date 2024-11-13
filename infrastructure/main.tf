# main.tf
provider "aws" {
  region = var.region
}

# VPC for MiniTwitter
resource "aws_vpc" "MiniTwitter_vpc" {
  cidr_block = var.vpc_cidr
  tags = {
    Name = "MiniTwitter-VPC"
  }
}

# Subnet for MiniTwitter
resource "aws_subnet" "MiniTwitter_subnet" {
  vpc_id = aws_vpc.MiniTwitter_vpc.id
  cidr_block = var.subnet_cidr
  tags = {
    Name = "MiniTwitter-Subnet"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "MiniTwitter_igw" {
  vpc_id = aws_vpc.MiniTwitter_vpc.id
  tags = {
    Name = "MiniTwitter-IGW"
  }
}

# Route Table
resource "aws_route_table" "MiniTwitter_route_table" {
  vpc_id = aws_vpc.MiniTwitter_vpc.id
  tags = {
    Name = "MiniTwitter-RouteTable"
  }

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.MiniTwitter_igw.id
  }
}

# Route Table Association
resource "aws_route_table_association" "MiniTwitter_rta" {
  subnet_id      = aws_subnet.MiniTwitter_subnet.id
  route_table_id = aws_route_table.MiniTwitter_route_table.id
}


# Security Group for MiniTwitter allowing SSH and gRPC (50051)
resource "aws_security_group" "MiniTwitter_sg" {
  vpc_id = aws_vpc.MiniTwitter_vpc.id
  tags = {
    Name = "MiniTwitter-SG"
  }

  # Allow SSH from anywhere
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow gRPC communication on port 50051
  ingress {
    from_port   = 50051
    to_port     = 50051
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound traffic (default all)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance to run MiniTwitter server
resource "aws_instance" "MiniTwitter_server" {
  ami                     = var.ami_id
  instance_type           = var.instance_type
  subnet_id               = aws_subnet.MiniTwitter_subnet.id
  vpc_security_group_ids  = [aws_security_group.MiniTwitter_sg.id]

  tags = {
    Name = "MiniTwitter-Server"
  }

  user_data = <<-EOF
              #!/bin/bash
              exec > /home/ec2-user/user_data.log 2>&1  # Log output to file for debugging

              # Wait for networking to be fully up
              sleep 10

              # Update packages and install dependencies
              sudo dnf update -y
              sudo dnf install -y python3 python3-pip git

              # Clone the repository and navigate into it
              if [ ! -d "/home/ec2-user/mini-twitter" ]; then
                  git clone https://github.com/MlCHAL-S/Minitwitter-private-test /home/ec2-user/mini-twitter
              fi
              cd /home/ec2-user/mini-twitter

              # Install Python dependencies
              sudo pip3 install -r requirements.txt

              # Set PYTHONPATH and run the server in the background
              export PYTHONPATH=/home/ec2-user/mini-twitter/src:$PYTHONPATH
              nohup python3 -m src.server.server &

              echo "MiniTwitter server setup complete"
  EOF
}

# Elastic IP for MiniTwitter server
resource "aws_eip" "MiniTwitter_eip" {
  instance = aws_instance.MiniTwitter_server.id
  tags = {
    Name = "MiniTwitter-EIP"
  }
}
