# Use the account's default network
data "aws_vpc" "default" {
  default = true
}

# Latest Amazon Linux 2023 image (64-bit Intel/AMD)
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

# Firewall: web traffic in, nothing else
resource "aws_security_group" "web" {
  name        = "cyberquest-web"
  description = "Allow web traffic to CyberQuest"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP (needed to issue the HTTPS certificate)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}