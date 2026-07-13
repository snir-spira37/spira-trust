terraform {
  required_version = ">= 1.15.0"
}

resource "terraform_data" "replaced" {
  input = {
    value = "v1"
  }
  triggers_replace = ["two"]

}
