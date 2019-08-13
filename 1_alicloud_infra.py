# PythonSDK https://developer.aliyun.com/tools/sdk#/python
#
# pip install aliyun-python-sdk-core aliyun-python-sdk-vpc aliyun-python-sdk-nas aliyun-python-sdk-ram
# pip install aliyun-python-sdk-cs aliyun-python-sdk-ecs
###############################################################


# coding=utf-8

import json
from aliyunsdkcore.client import AcsClient

#########################################
# APIコールのClientの作成
#########################################
REGION = "ap-northeast-1"
ACCESS_KEY_ID = "< Your Access Key ID >"
ACCESS_KEY_SECRET = "< Your Secret Key >"
client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)

###############################################################
# VPC
#   VPC, VSwitchの作成
###############################################################
# VPCの作成
from aliyunsdkvpc.request.v20160428.CreateVpcRequest import CreateVpcRequest

VPC_NAME="managed-k8s"
CIDER_BLOCK="192.168.0.0/16"

request = CreateVpcRequest()
request.set_accept_format('json')
request.set_CidrBlock(CIDER_BLOCK)
request.set_VpcName(VPC_NAME)

response = json.loads(client.do_action_with_exception(request))

# 確認
VPC_ID = response["VpcId"]
print(VPC_ID)
print("\n")
print(json.dumps(response, indent=4, sort_keys=True))

# VSwithの作成
from aliyunsdkvpc.request.v20160428.CreateVSwitchRequest import CreateVSwitchRequest

# 変数の準備
VSWITCH_CIRDER_BLOCK_1 = "192.168.10.0/24"
VSWITCH_CIRDER_BLOCK_2 = "192.168.20.0/24"
ZONE_ID_1 = "ap-northeast-1a"
ZONE_ID_2 = "ap-northeast-1b"

# VSwtich 1の作成
request = CreateVSwitchRequest()
request.set_accept_format('json')
request.set_CidrBlock(VSWITCH_CIRDER_BLOCK_1)
request.set_VpcId(VPC_ID)
request.set_ZoneId(ZONE_ID_1)

response = json.loads(client.do_action_with_exception(request))

# 確認
VSWITCH_ID_1 = response["VSwitchId"]
print("VSWITCH_ID_1 : " + VSWITCH_ID_1)
print("\n")
print(json.dumps(response, indent=4, sort_keys=True))

# VSwtich 2の作成
request.set_CidrBlock(VSWITCH_CIRDER_BLOCK_2)
request.set_ZoneId(ZONE_ID_2)

response = json.loads(client.do_action_with_exception(request))

# 確認
VSWITCH_ID_2 = response["VSwitchId"]
print("VSWITCH_ID_2 : " + VSWITCH_ID_2)
print("\n")
print(json.dumps(response, indent=4, sort_keys=True))


###############################################################
# NAS
#   File system, Access group, Access rule, Mount pointの作成
###############################################################

# NAS File Systemの作成
from aliyunsdknas.request.v20170626.CreateFileSystemRequest import CreateFileSystemRequest

request = CreateFileSystemRequest()
request.set_accept_format('json')
request.set_ProtocolType("NFS")
request.set_StorageType("Capacity")

response = json.loads(client.do_action_with_exception(request))

FILE_SYSTEM_ID = response["FileSystemId"]
print("FILE_SYSTEM_ID : ", FILE_SYSTEM_ID)
print("\n")
print(json.dumps(response, indent=4, sort_keys=True))

# NAS Access Group(Permission Group)の作成
from aliyunsdknas.request.v20170626.CreateAccessGroupRequest import CreateAccessGroupRequest

ACCESS_GROUP_NAME = "jupyter"

request = CreateAccessGroupRequest()
request.set_accept_format('json')
request.set_AccessGroupType("Vpc")
request.set_AccessGroupName(ACCESS_GROUP_NAME)

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response, indent=4, sort_keys=True))

# NAS Access Ruleの作成
from aliyunsdknas.request.v20170626.CreateAccessRuleRequest import CreateAccessRuleRequest

request = CreateAccessRuleRequest()
request.set_accept_format('json')

request.set_SourceCidrIp(CIDER_BLOCK)
request.set_AccessGroupName(ACCESS_GROUP_NAME)
request.set_RWAccessType("RDWR")
request.set_UserAccessType("no_squash")

response =  json.loads(client.do_action_with_exception(request))
print(json.dumps(response, indent=4, sort_keys=True))

# NAS Mount Pointの作成
from aliyunsdknas.request.v20170626.CreateMountTargetRequest import CreateMountTargetRequest

request = CreateMountTargetRequest()
request.set_accept_format('json')

request.set_AccessGroupName(ACCESS_GROUP_NAME)
request.set_NetworkType("VPC")
request.set_FileSystemId(FILE_SYSTEM_ID)
request.set_VpcId(VPC_ID)
request.set_VSwitchId(VSWITCH_ID_1)

response = json.loads(client.do_action_with_exception(request))

MOUNT_TARGET_DOMAIN = response["MountTargetDomain"]
print("MOUNT_TARGET_DOMAIN : ", MOUNT_TARGET_DOMAIN)
print("\n")
print(json.dumps(response, indent=4, sort_keys=True))

request.set_VSwitchId(VSWITCH_ID_2)
response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response, indent=4, sort_keys=True))

###############################################################
# RAM Role
#   K8s用のService Role / Policyの作成, RAM Policyの付与
###############################################################

# Roleの作成、信頼関係の付与
from aliyunsdkram.request.v20150501.CreateRoleRequest import CreateRoleRequest

CS_MANAGED_K8S_ROLE="AliyunCSManagedKubernetesRole"
ASSUME_ROLE_POLICY_DOCUMENT='''
{
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "cs.aliyuncs.com"
        ]
      }
    }
  ],
  "Version": "1"
}
'''

request = CreateRoleRequest()
request.set_accept_format('json')
request.set_RoleName(CS_MANAGED_K8S_ROLE)
request.set_AssumeRolePolicyDocument(ASSUME_ROLE_POLICY_DOCUMENT)

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response["Role"], indent=4, sort_keys=True))

# Roleの作成、信頼関係の付与
CS_AUDIT_ROLE="AliyunCSKubernetesAuditRole"

request.set_RoleName(CS_AUDIT_ROLE)

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response["Role"], indent=4, sort_keys=True))

# AliyunCSManagedKubernetesRolePolicyの作成
from aliyunsdkram.request.v20150501.CreatePolicyRequest import CreatePolicyRequest

request = CreatePolicyRequest()
request.set_accept_format('json')

CS_MANAGED_K8S_ROLE_POLICY = "AliyunCSManagedKubernetesRolePolicy"
request.set_PolicyName(CS_MANAGED_K8S_ROLE_POLICY)
POLICY_DOCUMENT = '''
{
  "Version": "1",
  "Statement": [
    {
      "Action": [
        "ecs:Describe*",
        "ecs:CreateRouteEntry",
        "ecs:DeleteRouteEntry",
        "ecs:CreateNetworkInterface",
        "ecs:DeleteNetworkInterface",
        "ecs:CreateNetworkInterfacePermission",
        "ecs:DeleteNetworkInterfacePermission"
      ],
      "Resource": [
        "*"
      ],
      "Effect": "Allow"
    },
    {
      "Action": [
        "slb:Describe*",
        "slb:CreateLoadBalancer",
        "slb:DeleteLoadBalancer",
        "slb:ModifyLoadBalancerInternetSpec",
        "slb:RemoveBackendServers",
        "slb:AddBackendServers",
        "slb:RemoveTags",
        "slb:AddTags",
        "slb:StopLoadBalancerListener",
        "slb:StartLoadBalancerListener",
        "slb:SetLoadBalancerHTTPListenerAttribute",
        "slb:SetLoadBalancerHTTPSListenerAttribute",
        "slb:SetLoadBalancerTCPListenerAttribute",
        "slb:SetLoadBalancerUDPListenerAttribute",
        "slb:CreateLoadBalancerHTTPSListener",
        "slb:CreateLoadBalancerHTTPListener",
        "slb:CreateLoadBalancerTCPListener",
        "slb:CreateLoadBalancerUDPListener",
        "slb:DeleteLoadBalancerListener",
        "slb:CreateVServerGroup",
        "slb:DescribeVServerGroups",
        "slb:DeleteVServerGroup",
        "slb:SetVServerGroupAttribute",
        "slb:DescribeVServerGroupAttribute",
        "slb:ModifyVServerGroupBackendServers",
        "slb:AddVServerGroupBackendServers",
        "slb:RemoveVServerGroupBackendServers"
      ],
      "Resource": [
        "*"
      ],
      "Effect": "Allow"
    },
    {
      "Action": [
        "vpc:Describe*",
        "vpc:DeleteRouteEntry",
        "vpc:CreateRouteEntry"
      ],
      "Resource": [
        "*"
      ],
      "Effect": "Allow"
    },
    {
      "Action": [
        "cr:Get*",
        "cr:List*",
        "cr:PullRepository"
      ],
      "Resource": "*",
      "Effect": "Allow"
    }
  ]
}
'''
request.set_PolicyDocument(POLICY_DOCUMENT)

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response, indent=4, sort_keys=True))

# AliyunCSKubernetesAuditRolePolicy の作成
CS_AUDIT_ROLE_POLICY="AliyunCSKubernetesAuditRolePolicy"
request.set_PolicyName(CS_AUDIT_ROLE_POLICY)
POLICY_DOCUMENT = '''
{
  "Version": "1",
  "Statement": [
    {
      "Action": [
        "log:CreateProject",
        "log:GetProject",
        "log:DeleteProject",
        "log:CreateLogStore",
        "log:GetLogStore",
        "log:UpdateLogStore",
        "log:DeleteLogStore",
        "log:CreateConfig",
        "log:UpdateConfig",
        "log:GetConfig",
        "log:DeleteConfig",
        "log:CreateMachineGroup",
        "log:UpdateMachineGroup",
        "log:GetMachineGroup",
        "log:DeleteMachineGroup",
        "log:ApplyConfigToGroup",
        "log:GetAppliedMachineGroups",
        "log:GetAppliedConfigs",
        "log:RemoveConfigFromMachineGroup",
        "log:CreateIndex",
        "log:GetIndex",
        "log:UpdateIndex",
        "log:DeleteIndex",
        "log:CreateSavedSearch",
        "log:GetSavedSearch",
        "log:UpdateSavedSearch",
        "log:DeleteSavedSearch",
        "log:CreateDashboard",
        "log:GetDashboard",
        "log:UpdateDashboard",
        "log:DeleteDashboard",
        "log:CreateJob",
        "log:GetJob",
        "log:DeleteJob",
        "log:UpdateJob"
      ],
      "Resource": "*",
      "Effect": "Allow"
    }
  ]
}
'''

request.set_PolicyDocument(POLICY_DOCUMENT)

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response, indent=4, sort_keys=True))

#　AliyunCSManagedKubernetesRole に AliyunCSManagedKubernetesRolePolicyを付与
from aliyunsdkram.request.v20150501.AttachPolicyToRoleRequest import AttachPolicyToRoleRequest

request = AttachPolicyToRoleRequest()
request.set_accept_format('json')

request.set_PolicyType("Custom")
request.set_PolicyName(CS_MANAGED_K8S_ROLE_POLICY)
request.set_RoleName(CS_MANAGED_K8S_ROLE)

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response, indent=4, sort_keys=True))

# AliyunCSKubernetesAuditRole に AliyunCSKubernetesAuditRolePolicy を付与
from aliyunsdkram.request.v20150501.AttachPolicyToRoleRequest import AttachPolicyToRoleRequest

request.set_PolicyName(CS_AUDIT_ROLE_POLICY)
request.set_RoleName(CS_AUDIT_ROLE)

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response, indent=4, sort_keys=True))


###############################################################
# ECS
#   Security Group, ECS Instanceの作成
###############################################################

# Security Groupの作成
from aliyunsdkecs.request.v20140526.CreateSecurityGroupRequest import CreateSecurityGroupRequest

request = CreateSecurityGroupRequest()
request.set_accept_format('json')
request.set_VpcId(VPC_ID)
response = json.loads(client.do_action_with_exception(request))

# 確認
SECURITY_GROUP_ID = response["SecurityGroupId"]
print("SECURITY_GROUP_ID : " , SECURITY_GROUP_ID)
print("\n")
print(json.dumps(response, indent=4, sort_keys=True))

# TODO: Bugの確認, Security rule を設定しても,ssh できない
# from aliyunsdkecs.request.v20140526.AuthorizeSecurityGroupRequest import AuthorizeSecurityGroupRequest

# request = AuthorizeSecurityGroupRequest()
# request.set_accept_format('json')

# SOURCE_CIDR_IP="202.45.12.165/32"
# request.set_SecurityGroupId(SECURITY_GROUP_ID)
# request.set_IpProtocol("tcp")
# request.set_PortRange("22/22")
# request.set_SourceCidrIp(SOURCE_CIDR_IP)
# request.set_SourcePortRange("22/22")
# request.set_Description("Frome SBC")

# response = client.do_action_with_exception(request)
# # python2:  print(response) 
# print(str(response, encoding='utf-8'))

# User data のエンコード
import base64

USER_DATA= '''#!/bin/bash
sudo yum update -y
sudo yum -y install nfs-utils
sudo mount -t nfs -o vers=3,nolock,proto=tcp 25543b48e13-jdd22.ap-northeast-1.nas.aliyuncs.com:/ /mnt
mkdir /mnt/shared-data
'''

ENCODE_USER_DATA = base64.b64encode(USER_DATA.encode('utf8'),)
print(ENCODE_USER_DATA.decode())

# ECS Instanceの作成
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest

# 変数の準備
IMAGE_ID = "centos_7_06_64_20G_alibase_20190711.vhd"
INSTANCE_TYPE = "ecs.t5-lc1m1.small"

# [ 注意 !!!! ] 初期のPasswordを更新し、パスワードポリシーに沿って運用すること 
PASSWORD=" " # Your SSH login Password. Password policy: [ 8 ~ 30文字 ] + [ 英字(大文字/小文字) + 数字 + 符号 ]のうちの3種類 

request = RunInstancesRequest()
request.set_accept_format('json')
request.set_ImageId(IMAGE_ID)
request.set_InstanceType(INSTANCE_TYPE)
request.set_SecurityGroupId(SECURITY_GROUP_ID)
request.set_VSwitchId(VSWITCH_ID)
request.set_ZoneId(ZONE_ID)
request.set_InstanceName("Jupyter_amin")
request.set_Password(PASSWORD)
request.set_InternetMaxBandwidthIn(200)
request.set_InternetMaxBandwidthOut(100)
request.set_UserData(ENCODE_USER_DATA)
response = json.loads(client.do_action_with_exception(request))

print(json.dumps(response, indent=4, sort_keys=True))

###############################################################
# K8s
#   K8s Clusterの作成
###############################################################

# TODO
# Python SDKで K8s Cluster構築

# aliyun cli実行環境を準備
# aliyun cs POST /clusters --body "$(cat jupyter-k8s.json)"
 


