terraform {
  required_version = ">= 1.15.0"
}

resource "terraform_data" "replaced_cbd" {
  input = {
    value = "v1"
  }
  triggers_replace = ["two"]

  lifecycle {
    create_before_destroy = true
  }

}
