variable "region" {
  default = "eu-central-1"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "subnet_cidr" {
  default = "10.0.1.0/24"
}

variable "ami_id" {
  description = "Amazon Machine Image ID for Ubuntu"
  default     = "ami-0eddb4a4e7d846d6f"
}

variable "instance_type" {
  default = "t2.micro"
}
