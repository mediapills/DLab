#!/bin/bash
# *****************************************************************************
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# ******************************************************************************

set -ex

check_tokens () {
RUN=$(aws s3 ls s3://${k8s-bucket-name}/k8s/masters/ > /dev/null && echo "true" || echo "false")
sleep 5
}

check_elb_status () {
RUN=$(aws elbv2 describe-target-health --target-group-arn ${k8s-tg-arn} --region ${k8s-region} | \
     jq -r '.TargetHealthDescriptions[].TargetHealth.State' | \
     grep "^healthy" > /dev/null && echo "true" || echo "false")
sleep 5
}

# Creating DLab user
sudo useradd -m -G sudo -s /bin/bash ${k8s_os_user}
sudo bash -c 'echo "${k8s_os_user} ALL = NOPASSWD:ALL" >> /etc/sudoers'
sudo mkdir /home/${k8s_os_user}/.ssh
sudo bash -c 'cat /home/ubuntu/.ssh/authorized_keys > /home/${k8s_os_user}/.ssh/authorized_keys'
sudo chown -R ${k8s_os_user}:${k8s_os_user} /home/${k8s_os_user}/
sudo chmod 700 /home/${k8s_os_user}/.ssh
sudo chmod 600 /home/${k8s_os_user}/.ssh/authorized_keys

sudo apt-get update
sudo apt-get install -y python-pip jq unzip
sudo apt-get install -y default-jre
sudo apt-get install -y default-jdk
sudo pip install -U pip
sudo pip install awscli

local_ip=$(curl http://169.254.169.254/latest/meta-data/local-ipv4)
first_master_ip=$(aws autoscaling describe-auto-scaling-instances --region ${k8s-region} --output text --query \
                 "AutoScalingInstances[?AutoScalingGroupName=='${k8s-asg}'].InstanceId" | xargs -n1 aws ec2 \
                 describe-instances --instance-ids $ID --region ${k8s-region} --query \
                 "Reservations[].Instances[].PrivateIpAddress" --output text | sort | head -n1)

# installing Docker
sudo bash -c 'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -'
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce
sudo systemctl enable docker
# installing kubeadm, kubelet and kubectl
sudo apt-get install -y apt-transport-https curl
sudo bash -c 'curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -'
sudo bash -c 'echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list'
sudo apt-get update
sudo apt-get install -y kubelet=${kubernetes_version} kubeadm=${kubernetes_version} kubectl=${kubernetes_version}

check_tokens
if [[ $local_ip == "$first_master_ip" ]] && [[ $RUN == "false" ]];then
cat <<EOF > /tmp/kubeadm-config.yaml
apiVersion: kubeadm.k8s.io/v1beta2
kind: ClusterConfiguration
kubernetesVersion: stable
apiServerCertSANs:
  - ${k8s-nlb-dns-name}
controlPlaneEndpoint: "${k8s-nlb-dns-name}:6443"
EOF
sudo kubeadm init --config=/tmp/kubeadm-config.yaml --upload-certs
while check_elb_status
do
    if [[ $RUN == "false" ]];
    then
        echo "Waiting for NLB healthy status..."
    else
        echo "LB status is healthy!"
        break
    fi
done
sudo mkdir -p /home/${k8s_os_user}/.kube
sudo cp -i /etc/kubernetes/admin.conf /home/${k8s_os_user}/.kube/config
sudo chown -R ${k8s_os_user}:${k8s_os_user} /home/${k8s_os_user}/.kube
sudo kubeadm token create --print-join-command > /tmp/join_command
sudo kubeadm init phase upload-certs --upload-certs | grep -v "upload-certs" > /tmp/cert_key
sudo -i -u ${k8s_os_user} kubectl apply -f \
     "https://cloud.weave.works/k8s/net?k8s-version=$(sudo -i -u ${k8s_os_user} kubectl version | base64 | tr -d '\n')"
sudo -i -u ${k8s_os_user} bash -c 'curl -L https://git.io/get_helm.sh | bash'
cat <<EOF > /tmp/rbac-config.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tiller
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: tiller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: tiller
    namespace: kube-system
EOF
sudo -i -u ${k8s_os_user} kubectl create -f /tmp/rbac-config.yaml
sudo -i -u ${k8s_os_user} helm init --service-account tiller --history-max 200
# Generating Java SSL certs
sudo mkdir -p /home/${k8s_os_user}/keys
sudo keytool -genkeypair -alias dlab -keyalg RSA -validity 730 -storepass ${ssn_keystore_password} \
  -keypass ${ssn_keystore_password} -keystore /home/${k8s_os_user}/keys/ssn.keystore.jks \
  -keysize 2048 -dname "CN=${k8s-nlb-dns-name}" -ext SAN=dns:localhost,dns:${k8s-nlb-dns-name}
sudo keytool -exportcert -alias dlab -storepass ${ssn_keystore_password} -file /home/${k8s_os_user}/keys/ssn.crt \
  -keystore /home/${k8s_os_user}/keys/ssn.keystore.jks

aws s3 cp /home/${k8s_os_user}/keys/ssn.keystore.jks s3://${k8s-bucket-name}/dlab/certs/ssn/ssn.keystore.jks
aws s3 cp /home/${k8s_os_user}/keys/ssn.crt s3://${k8s-bucket-name}/dlab/certs/ssn/ssn.crt

sudo keytool -genkeypair -alias dlab -keyalg RSA -validity 730 -storepass ${endpoint_keystore_password} \
  -keypass ${endpoint_keystore_password} -keystore /home/${k8s_os_user}/keys/endpoint.keystore.jks \
  -keysize 2048 -dname "CN=${endpoint_elastic_ip}" -ext SAN=dns:localhost,dns:${endpoint_elastic_ip}
sudo keytool -exportcert -alias dlab -storepass ${endpoint_keystore_password} -file /home/${k8s_os_user}/keys/endpoint.crt \
  -keystore /home/${k8s_os_user}/keys/endpoint.keystore.jks

aws s3 cp /home/${k8s_os_user}/keys/endpoint.keystore.jks s3://${k8s-bucket-name}/dlab/certs/endpoint/endpoint.keystore.jks
aws s3 cp /home/${k8s_os_user}/keys/endpoint.crt s3://${k8s-bucket-name}/dlab/certs/endpoint/endpoint.crt
sleep 60
aws s3 cp /tmp/join_command s3://${k8s-bucket-name}/k8s/masters/join_command
aws s3 cp /tmp/cert_key s3://${k8s-bucket-name}/k8s/masters/cert_key
sudo rm -f /tmp/join_command
sudo rm -f /tmp/cert_key
else
while check_tokens
do
    if [[ $RUN == "false" ]];
    then
        echo "Waiting for initial cluster initialization..."
    else
        echo "Initial cluster initialized!"
        break
    fi
done
aws s3 cp s3://${k8s-bucket-name}/k8s/masters/join_command /tmp/join_command
aws s3 cp s3://${k8s-bucket-name}/k8s/masters/cert_key /tmp/cert_key
join_command=$(cat /tmp/join_command)
cert_key=$(cat /tmp/cert_key)
sudo $join_command --control-plane --certificate-key "$cert_key"
sudo mkdir -p /home/${k8s_os_user}/.kube
sudo cp -i /etc/kubernetes/admin.conf /home/${k8s_os_user}/.kube/config
sudo chown -R ${k8s_os_user}:${k8s_os_user} /home/${k8s_os_user}/.kube
sudo -i -u ${k8s_os_user} bash -c 'curl -L https://git.io/get_helm.sh | bash'
sudo -i -u ${k8s_os_user} helm init --client-only --history-max 200
fi
cat <<EOF > /tmp/update_files.sh
#!/bin/bash
sudo kubeadm token create --print-join-command > /tmp/join_command
sudo kubeadm init phase upload-certs --upload-certs | grep -v "upload-certs" > /tmp/cert_key
aws s3 cp /tmp/join_command s3://${k8s-bucket-name}/k8s/masters/join_command
aws s3 cp /tmp/cert_key s3://${k8s-bucket-name}/k8s/masters/cert_key
sudo rm -f /tmp/join_command
sudo rm -f /tmp/cert_key
EOF
sudo mv /tmp/update_files.sh /usr/local/bin/update_files.sh
sudo chmod 755 /usr/local/bin/update_files.sh
sudo bash -c 'echo "0 0 * * * root /usr/local/bin/update_files.sh" >> /etc/crontab'

#cat <<EOF > /tmp/remove-etcd-member.sh
##!/bin/bash
#hostname=\$(/bin/hostname)
#not_ready_node=\$(/usr/bin/sudo -i -u ${k8s_os_user} /usr/bin/kubectl get nodes | grep NotReady | grep master | awk '{print \$1}')
#if [[ \$not_ready_node != "" ]]; then
#etcd_pod_name=\$(/usr/bin/sudo -i -u ${k8s_os_user} /usr/bin/kubectl get pods -n kube-system | /bin/grep etcd \
#    | /bin/grep "\$hostname" | /usr/bin/awk '{print \$1}')
#etcd_member_id=\$(/usr/bin/sudo -i -u ${k8s_os_user} /usr/bin/kubectl -n kube-system exec -it \$etcd_pod_name \
#    -- /bin/sh -c "ETCDCTL_API=3 etcdctl member list --endpoints=https://[127.0.0.1]:2379 \
#    --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
#    --key=/etc/kubernetes/pki/etcd/healthcheck-client.key"  | /bin/grep ", \$not_ready_node" | /usr/bin/awk -F',' '{print \$1}')
#/usr/bin/sudo -i -u ${k8s_os_user} /usr/bin/kubectl -n kube-system exec -it \$etcd_pod_name \
#    -- /bin/sh -c "ETCDCTL_API=3 etcdctl member remove \$etcd_member_id --endpoints=https://[127.0.0.1]:2379 \
#    --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
#    --key=/etc/kubernetes/pki/etcd/healthcheck-client.key"
#/usr/bin/sudo -i -u ${k8s_os_user} /usr/bin/kubectl delete node \$not_ready_node
#
#fi
#
#EOF
# sudo mv /tmp/remove-etcd-member.sh /usr/local/bin/remove-etcd-member.sh
# sudo chmod 755 /usr/local/bin/remove-etcd-member.sh
# sleep 300
# sudo bash -c 'echo "* * * * * root /usr/local/bin/remove-etcd-member.sh >> /var/log/cron_k8s.log 2>&1" >> /etc/crontab'
sudo -i -u ${k8s_os_user} helm repo update
wget https://releases.hashicorp.com/terraform/0.12.3/terraform_0.12.3_linux_amd64.zip -O /tmp/terraform_0.12.3_linux_amd64.zip
unzip /tmp/terraform_0.12.3_linux_amd64.zip -d /tmp/
sudo mv /tmp/terraform /usr/local/bin/
