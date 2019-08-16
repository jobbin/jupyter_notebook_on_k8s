##################################################
# Sensitive info
##################################################
access_key      = ""
secret_key      = ""
worker_password = ""
ecs_password    = ""
ssh_ip          = ""

##################################################
# Region, AZ
##################################################
region = "ap-northeast-1"
zone_a = "ap-northeast-1a"
zone_b = "ap-northeast-1b"

##################################################
# VPC 関連
##################################################
vpc_name                = "jupyter-vpc"
vpc_cidr_block          = "192.168.0.0/16"
vswitch_1_name          = "zone_a"
vswitch_1_cidr_block    = "192.168.1.0/24"
vswitch_2_name          = "zone_b"
vswitch_2_cidr_block    = "192.168.2.0/24"

##################################################
# NAT Gateway 関連
##################################################
nat_gateway_name            = "jupyter-nat-gw"
nat_gateway_specification   = "Small"

##################################################
# NAS 関連
##################################################
nas_access_group_name = "jupyter_access"

##################################################
# Log Service 関連
##################################################
log_project = "log-jupyter-on-k8s"

##################################################
# ACK 関連
##################################################
# The name must be 1 to 63 characters in length 
# and can contain numbers, Chinese characters, letters, and hyphens (-).
ack_cluster_name        = "jupyter-on-k8s"
worker_instance_type    = "ecs.sn1ne.xlarge"
worker_num              = "2"
k8s_pod_cidr            = "172.20.0.0/16"
k8s_service_cidr        = "172.21.0.0/20"
worker_disk_category    = "cloud_efficiency"
worker_data_disk_size   = "100"
cluster_network_type    = "terway"

##################################################
# 管理用ECS 関連
##################################################
ecs_instance_name               = "jupyter_admin"
ecs_instance_type               = "ecs.t5-lc1m1.small"
ecs_system_disk_category        = "cloud_efficiency"
ecs_image_id                    = "centos_7_06_64_20G_alibase_20190711.vhd"
ecs_internet_max_bandwidth_out  = "100"
port_range                      = "22/22"
