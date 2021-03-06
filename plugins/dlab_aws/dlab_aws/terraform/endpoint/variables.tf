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

variable "service_base_name" {}

variable "access_key_id" {
  default = ""
}
variable "secret_access_key" {
  default = ""
}

variable "region" {}

variable "zone" {}

variable "product" {}

variable "subnet_cidr" {}

variable "endpoint_instance_shape" {}

variable "key_name" {}

variable "ami" {}

variable "vpc_id" {}

variable "ssn_subnet" {}

variable "network_type" {}

variable "vpc_cidr" {}

variable "endpoint_volume_size" {}

variable "endpoint_eip_allocation_id" {}

variable "endpoint_id" {}

variable "additional_tag" {
  default = "product:dlab"
}

variable "tag_resource_id" {
  default = "user:tag"
}
