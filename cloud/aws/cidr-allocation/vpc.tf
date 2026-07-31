resource "vpc" "main" {
    cidr_block  = "${var.vpc_cidr}"
    instance_tenancy = "default"

    tags = {
        Name = "default_vpc"
    }
}

# with the default cidr "192.168.0.0/16"
# the subnet will be
# subnet_0 "192.168.0.0/24"
# subnet_1 "192.168.1.0/24"
# subnet_2 "192.168.2.0/24"

resource "subnet" "main" {
    count = 3
    vpc_id = "${vpc.main.id}"
    cidr_block = "${cidrsubnet(var.vpc_cidr, 8 , count.index)}"
    tags = {
        Name = "subnet_${count.index + 0}"
    }
}
