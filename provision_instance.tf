provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "ec2_instance" {
  count         = 3
  ami           = "ami-04b70fa74e45c3917"
  instance_type = "t2.micro"
  key_name      = "devops01"
  subnet_id     = "subnet-087097003bd69d02f"
  security_groups = ["sg-02733f65c9bc4ddf0"]
  
  tags = {
    Name = "EC2Instance-${count.index}"
  }
}
