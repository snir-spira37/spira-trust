terraform {
  required_version = ">= 1.15.0"
}

resource "terraform_data" "updated" {
  input = {
    value = "v2"
  }
}
