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

variable "access_key_id" {}

variable "secret_access_key" {}

variable "service_base_name" {}

variable "project_name" {}

variable "project_tag" {}

variable "endpoint_tag" {}

variable "user_tag" {}

variable "custom_tag" {}

variable "region" {}

variable "zone" {}

variable "vpc_id" {}

variable "subnet_id" {}

variable "nb_cidr" {}

variable "edge_cidr" {}

variable "ami" {}

variable "instance_type" {}

variable "key_name" {}

variable "edge_volume_size" {}

variable "additional_tag" {
  default = "product:dlab"
}

variable "tag_resource_id" {
  default = "user:tag"
}