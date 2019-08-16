#!/bin/bash
#
# 2019/08 created by Qiu
# -----------------------------------------------
# Description:
#
#
# Usage:
#  $ ./2_kubectl_apply.sh <The num of user> <Cluster domain>
#
# Params:
#  <The num of user>    :    2
#  <Cluster domain>     :   *******.ap-northeast-1.alicontainer.com
#
# -----------------------------------------------


PARAMS=$#

# Jupyterを利用するユーザーの数
NUM_USER=$1

# K8s ClusterのDomain
CLUSTER_DOMAIN=$2

# 設定前のJupyter file
JUPYTER_TEPLATE_YAML="./0_jupyter-user-template.yaml"

# 設定前のIngress yaml
INGRESS_YAML="./0_ingress.yaml"

# Ingress rule template
INGRESS_RULE="./0_rules_template.txt"

# Namespace
NAMESPACE="jupyter"

# ====================================================
# Usage
# ====================================================
function usage() {
cat <<_EOT_

Usage:
  $ $0 <The num of user> <Cluster domain>
Params:
  <The num of user>    :    2
  <Cluster domain>     :   *******.ap-northeast-1.alicontainer.com

_EOT_
exit 1
}

# ====================================================
# Check params
# ====================================================
function check_params () {

  if [ ${1} != 2 ]; then 
    usage
  fi
  return 0
}

# ====================================================
# Start
# ====================================================

# paramsの確認
check_params ${PARAMS}

######################################
# UserごとにDeployment, Serviceの作成
######################################
for ((i=1;i<=${NUM_USER};i++))
do
    response=`cat ${JUPYTER_TEPLATE_YAML} | sed s/JUPYTER_USER/user$i/`
    echo -e "--------------- YAML of user$i --------------- \n"
    echo "${response}"
    echo -e "---------------------------------------------- \n"
    echo -e "----- kubectl apply -f YAML of user$i -----"
    cat ${JUPYTER_TEPLATE_YAML} | sed s/JUPYTER_USER/user$i/ | kubectl apply -n ${NAMESPACE} -f -
    echo -e "----------------------------------------------\n"
done

######################################
# Ingress の作成
######################################
cat ${INGRESS_YAML} > .ingress.yaml
for ((i=1;i<=${NUM_USER};i++))
do
    cat ${INGRESS_RULE} | sed s/JUPYTER_USER/user${i}/ | sed s/CLUSTER_DOMAIN/${CLUSTER_DOMAIN}/ >> .ingress.yaml
done
echo -e "--------------- Ingress YAML ---------------"
cat .ingress.yaml
kubectl apply -n ${NAMESPACE} -f .ingress.yaml
echo -e "------------------------------------------- \n"

######################################
# TODO -> PodのStatusの確認
######################################
# while ${not_running_status}==true
# do
#     tmp_data=`kubectl get po | grep user | cut -d ' ' -f 9`
#     array_status=(`echo $tmp_data`)
#     sleep 3
# done

sleep 10s
######################################
# Jupyter の Token を取得
######################################
echo -e "--------------- Toke of pod ---------------"
pod_data=`kubectl get po -n ${NAMESPACE} | grep user | cut -d ' ' -f 1`
array_pod=(`echo ${pod_data}`)
for pod in ${array_pod[@]}
do
    token=`kubectl logs $pod -n ${NAMESPACE} | grep "] http://user" | cut -d '=' -f 2`
    echo "${pod} : ${token}"    
done
echo -e "------------------------------------------- \n"