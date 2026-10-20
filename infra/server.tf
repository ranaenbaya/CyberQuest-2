resource "random_password" "secret_key" {
  length  = 48
  special = false
}

resource "random_password" "db_password" {
  length  = 32
  special = false
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = var.instance_type
  vpc_security_group_ids      = [aws_security_group.web.id]
  associate_public_ip_address = true

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    secret_key  = random_password.secret_key.result
    db_password = random_password.db_password.result
    image       = var.image
  })
  user_data_replace_on_change = true

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name = "cyberquest"
  }
}