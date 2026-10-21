variable "region" {
  type    = string
  default = "eu-north-1"
}

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "image" {
  type    = string
  default = "ghcr.io/ranaenbaya/cyberquest-2:latest"
}