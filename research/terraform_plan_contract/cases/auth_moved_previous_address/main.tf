terraform {
  required_version = ">= 1.15.0"
}

moved {
  from = terraform_data.old
  to   = terraform_data.new
}

resource "terraform_data" "new" {
  input = {
    value = "v1"
  }
}
