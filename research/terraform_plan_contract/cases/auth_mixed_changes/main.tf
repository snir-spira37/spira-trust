terraform {
  required_version = ">= 1.15.0"
}

resource "terraform_data" "updated" {
  input = {
    value = "v2"
  }
}

resource "terraform_data" "created" {
  input = {
    value = "v1"
  }
}
