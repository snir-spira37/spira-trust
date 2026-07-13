terraform {
  required_version = ">= 1.15.0"
}

resource "terraform_data" "stable" {
  input = {
    value = "v1"
  }
}
