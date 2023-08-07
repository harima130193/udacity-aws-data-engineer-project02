resource "aws_vpc" "redshift_vpc" {
  cidr_block = var.vpc_cidr

  instance_tenancy = "default"
  tags = {
    Name = "redshift-vpc"
  }
}

resource "aws_internet_gateway" "redshift_vpc_gw" {

  vpc_id = aws_vpc.redshift_vpc.id

  depends_on = [

    aws_vpc.redshift_vpc

  ]

}

resource "aws_route_table" "redshift_pub_route_table" {
  vpc_id = aws_vpc.redshift_vpc.id


  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.redshift_vpc_gw.id
  }

  tags = {
    Name = "redshift-route-table"
  }
  depends_on = [
    aws_vpc.redshift_vpc,
    aws_internet_gateway.redshift_vpc_gw
  ]
}

resource "aws_security_group" "redshift_security_group" {

  vpc_id = aws_vpc.redshift_vpc.id

  ingress {

    from_port = 5439

    to_port = 5439

    protocol = "tcp"

    cidr_blocks = [var.my_ip_address_cidr]

  }

  egress {
    from_port   = 0

    to_port     = 0

    protocol    = "-1"

    cidr_blocks = ["0.0.0.0/0"]

  }


  tags = {

    Name = "redshift-sg"

  }

  depends_on = [

    aws_vpc.redshift_vpc

  ]

}

resource "aws_subnet" "redshift_subnet_1" {

  vpc_id = aws_vpc.redshift_vpc.id

  cidr_block = var.redshift_subnet_cidr_first

  availability_zone = var.redshift_subnet_az_1

  map_public_ip_on_launch = true

  tags = {

    Name = "redshift-subnet-1"

  }

  depends_on = [

    aws_vpc.redshift_vpc

  ]

}

resource "aws_subnet" "redshift_subnet_2" {

  vpc_id = aws_vpc.redshift_vpc.id

  cidr_block = var.redshift_subnet_cidr_second

  availability_zone = var.redshift_subnet_az_2

  map_public_ip_on_launch = true

  tags = {

    Name = "redshift-subnet-2"

  }

  depends_on = [

    aws_vpc.redshift_vpc

  ]

}

resource "aws_route_table_association" "redshift_subnet_1_route" {
  subnet_id      = aws_subnet.redshift_subnet_1.id
  route_table_id = aws_route_table.redshift_pub_route_table.id
  depends_on = [
    aws_route_table.redshift_pub_route_table,
    aws_subnet.redshift_subnet_1
  ]
}

resource "aws_route_table_association" "redshift_subnet_2_route" {
  subnet_id      = aws_subnet.redshift_subnet_2.id
  route_table_id = aws_route_table.redshift_pub_route_table.id
  depends_on = [
    aws_route_table.redshift_pub_route_table,
    aws_subnet.redshift_subnet_2
  ]
}

resource "aws_redshift_subnet_group" "redshift_subnet_group" {

  name = "redshift-subnet-group"

  subnet_ids = [aws_subnet.redshift_subnet_1.id, aws_subnet.redshift_subnet_2.id]

  tags = {

    environment = "dev"

    Name = "redshift-subnet-group"

  }
}

resource "aws_iam_role" "redshift_role" {

  name = "redshift_role"

  assume_role_policy = data.aws_iam_policy_document.redshift_assume_role.json

  tags = {

    tag-key = "redshift-role"

  }

}


resource "aws_iam_role_policy" "s3_read_only_policy" {

  name = "redshift_s3_policy"

  role = aws_iam_role.redshift_role.id

  policy = data.aws_iam_policy_document.public_read_access.json

}

resource "aws_redshift_cluster" "default" {

  cluster_identifier = var.rs_cluster_identifier

  database_name = var.rs_database_name

  master_username = var.rs_master_username

  master_password = var.rs_master_pass

  node_type = var.rs_nodetype

  cluster_type = var.rs_cluster_type

  cluster_subnet_group_name = aws_redshift_subnet_group.redshift_subnet_group.name

  skip_final_snapshot = true
  
  publicly_accessible = true

  vpc_security_group_ids = [aws_security_group.redshift_security_group.id]

  iam_roles = [aws_iam_role.redshift_role.arn]

  depends_on = [

    aws_vpc.redshift_vpc,

    aws_security_group.redshift_security_group,

    aws_redshift_subnet_group.redshift_subnet_group,

    aws_iam_role.redshift_role

  ]

}