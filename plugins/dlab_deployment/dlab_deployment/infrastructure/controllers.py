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
from api.managers import APIManager
from dlab_core.domain.entities import STATUS_PROCESSED, STATUS_BAD_REQUEST
from dlab_core.infrastructure.controllers import (
    BaseCLIController, BaseAPIController)
from dlab_core.infrastructure.schema_validator import validate_schema
from dlab_deployment.infrastructure.schemas import CREATE_PROJECT_SCHEMA

START = 'start'
STOP = 'stop'
DEPLOY = 'deploy'


class BaseDeploymentCLIController(BaseCLIController):
    @staticmethod
    def deploy_ssn():
        raise NotImplementedError

    @staticmethod
    def destroy_ssn():
        raise NotImplementedError

    @classmethod
    def deploy_endpoint(cls):
        raise NotImplementedError

    @classmethod
    def destroy_endpoint(cls):
        raise NotImplementedError


class APIProjectsController(BaseAPIController):
    allowed_actions = [START, STOP]

    @classmethod
    def create_project(cls, request):
        is_valid = validate_schema(request.json, CREATE_PROJECT_SCHEMA)
        if is_valid:
            manager = APIManager()
            record_id = manager.create_record(
                request.json, request.blueprint, DEPLOY
            )
            return {'code': record_id}, STATUS_PROCESSED

        return {"code": is_valid, "message": "string"}, STATUS_BAD_REQUEST

    @classmethod
    def get_project(cls, name):
        return {"status": "running", "error_message": "string"}

    @classmethod
    def update_project(cls, name, **kwargs):
        action = kwargs.get('action')
        if action not in cls.allowed_actions:
            return {"code": 0, "message": "string"}, STATUS_BAD_REQUEST

        # TODO: handle not found
        # if not found:
        #     return {"code": 0, "message": "string"}, 404

        status = cls.do_action(action)
        return {'status': status}, STATUS_PROCESSED

    @classmethod
    def delete_project(cls, name):
        # TODO: handle not found
        # if not found:
        #     return {"code": 0, "message": "string"}, 404
        return {}, STATUS_PROCESSED

    @classmethod
    def do_action(cls, action):
        status = 1
        if action == START:
            pass
        if action == STOP:
            pass
        return status
