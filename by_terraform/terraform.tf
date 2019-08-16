##################################################
# Sensitive info
##################################################
variable "access_key" {}
variable "secret_key" {}
variable ecs_password {}
variable ssh_ip {}

##################################################
# Region, AZ
##################################################
variable "region" {}
variable "zone_a" {}
variable "zone_b" {}

##################################################
# VPC 関連
##################################################
variable "vpc_name" {}
variable "vpc_cidr_block" {}
variable "vswitch_1_name" {}
variable "vswitch_1_cidr_block" {}
variable "vswitch_2_name" {}
variable "vswitch_2_cidr_block" {}

##################################################
# NAT Gateway 関連
##################################################
variable nat_gateway_name {}
variable nat_gateway_specification {}

##################################################
# NAS 関連
##################################################
variable nas_access_group_name {}

##################################################
# Log Service 関連
##################################################
variable "log_project" {}

##################################################
# ACK 関連
##################################################
variable ack_cluster_name {}
variable worker_instance_type {}
variable worker_num {}
variable worker_password {}
variable k8s_pod_cidr {}
variable k8s_service_cidr {}
variable worker_disk_category {}
variable worker_data_disk_size {}
variable cluster_network_type {}

##################################################
# 管理用ECS 関連
##################################################
variable ecs_instance_name {}
variable ecs_instance_type {}
variable ecs_system_disk_category {}
variable ecs_image_id {}
variable ecs_internet_max_bandwidth_out {}
variable port_range {}


##################################################
# AliCloud Providerの設定
##################################################
provider "alicloud" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region = "${var.region}"
}

############################################
# VPC関連
############################################
resource "alicloud_vpc" "vpc" {
  name = "${var.vpc_name}"
  cidr_block = "${var.vpc_cidr_block}"
}

resource "alicloud_vswitch" "vswitch_1" {
  name              = "${var.vswitch_1_name}"
  vpc_id            = "${alicloud_vpc.vpc.id}"
  cidr_block        = "${var.vswitch_1_cidr_block}"
  availability_zone = "${var.zone_a}"
}

resource "alicloud_vswitch" "vswitch_2" {
  name              = "${var.vswitch_2_name}"
  vpc_id            = "${alicloud_vpc.vpc.id}"
  cidr_block        = "${var.vswitch_2_cidr_block}"
  availability_zone = "${var.zone_b}"
}

############################################
# NAT Gateway関連
############################################
resource "alicloud_eip" "nat_eip" {
  internet_charge_type = "PayByTraffic"
}

resource "alicloud_eip_association" "nat_eip_asso" {
  allocation_id = "${alicloud_eip.nat_eip.id}"
  instance_id   = "${alicloud_nat_gateway.nat_gateway.id}"
}

resource "alicloud_nat_gateway" "nat_gateway" {
  vpc_id        = "${alicloud_vpc.vpc.id}"
  specification = "${var.nat_gateway_specification}"
  name          = "${var.nat_gateway_name}"
}

resource "alicloud_snat_entry" "snat_entry_1" {
  snat_table_id     = "${alicloud_nat_gateway.nat_gateway.snat_table_ids}"
  source_vswitch_id = "${alicloud_vswitch.vswitch_1.id}"
  snat_ip           = "${alicloud_eip.nat_eip.ip_address}"
}

resource "alicloud_snat_entry" "snat_entry_2" {
  snat_table_id     = "${alicloud_nat_gateway.nat_gateway.snat_table_ids}"
  source_vswitch_id = "${alicloud_vswitch.vswitch_2.id}"
  snat_ip           = "${alicloud_eip.nat_eip.ip_address}"
}

############################################
# NAS関連
############################################
resource "alicloud_nas_file_system" "jupyter_nas" {
  protocol_type = "NFS"
  storage_type  = "Capacity"
}

resource "alicloud_nas_access_group" "jupyter_access_group" {
  name        = "${var.nas_access_group_name}"
  type        = "Vpc"
}

resource "alicloud_nas_access_rule" "jupyter_access_rule-1" {
  access_group_name = "${alicloud_nas_access_group.jupyter_access_group.id}"
  source_cidr_ip    = "${alicloud_vswitch.vswitch_1.cidr_block}"
  rw_access_type    = "RDONLY"
  user_access_type  = "all_squash"
  priority          = 2

}

resource "alicloud_nas_mount_target" "jupyter_mount_target_vs1" {
  file_system_id    = "${alicloud_nas_file_system.jupyter_nas.id}"
  access_group_name = "${alicloud_nas_access_group.jupyter_access_group.id}"
  vswitch_id        = "${alicloud_vswitch.vswitch_1.id}"
}

resource "alicloud_nas_mount_target" "jupyter_mount_target_vs2" {
  file_system_id    = "${alicloud_nas_file_system.jupyter_nas.id}"
  access_group_name = "${alicloud_nas_access_group.jupyter_access_group.id}"
  vswitch_id        = "${alicloud_vswitch.vswitch_2.id}"
}

############################################
# Log Service関連
############################################
resource "alicloud_log_project" "log_project" {
  name        = "${var.log_project}"
}

############################################
# ACK Cluster関連
############################################
resource "alicloud_cs_managed_kubernetes" "managed_k8s" {
  name                  = "${var.ack_cluster_name}"
  worker_instance_types = ["${var.worker_instance_type}"]
  vswitch_ids           = ["${alicloud_vswitch.vswitch_1.id}", "${alicloud_vswitch.vswitch_2.id}"]
  worker_number         = "${var.worker_num}"
  password              = "${var.worker_password}"
  pod_cidr              = "${var.k8s_pod_cidr}"
  service_cidr          = "${var.k8s_service_cidr}"
  new_nat_gateway       = false
  install_cloud_monitor = true
  slb_internet_enabled  = true
  worker_disk_category  = "${var.worker_disk_category}"
  worker_data_disk_size = "${var.worker_data_disk_size}"
  cluster_network_type  = "${var.cluster_network_type}"
}

############################################
# 管理用ECS関連
############################################
resource "alicloud_security_group" "jupyter_admin_group" {
  name        = "${var.ecs_instance_name}"
  vpc_id      = "${alicloud_vpc.vpc.id}"
}

resource "alicloud_security_group_rule" "allow_ssh" {
  type              = "ingress"
  ip_protocol       = "tcp"
  nic_type          = "intranet"
  policy            = "accept"
  port_range        = "${var.port_range}"
  priority          = 1
  security_group_id = "${alicloud_security_group.jupyter_admin_group.id}"
  cidr_ip           = "${var.ssh_ip}"
}

resource "alicloud_instance" "instance" {
  availability_zone = "ap-northeast-1a"
  security_groups   = "${alicloud_security_group.jupyter_admin_group.*.id}"
  instance_name              = "${var.ecs_instance_name}"
  instance_type              = "${var.ecs_instance_type}"
  system_disk_category       = "${var.ecs_system_disk_category}"
  image_id                   = "${var.ecs_image_id}"
  vswitch_id                 = "${alicloud_vswitch.vswitch_1.id}"
  internet_max_bandwidth_out = "${var.ecs_internet_max_bandwidth_out}"
  internet_charge_type       = "PayByTraffic"
  instance_charge_type       = "PostPaid"
  password                   = "${var.ecs_password}"
}