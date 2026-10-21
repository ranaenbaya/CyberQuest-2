output "site_url" {
  value = "https://${replace(aws_instance.app.public_ip, ".", "-")}.sslip.io"
}

output "instance_id" {
  value = aws_instance.app.id
}
