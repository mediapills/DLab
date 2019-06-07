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

import abc
import six
from jsonschema import validate, exceptions


@six.add_metaclass(abc.ABCMeta)
class BaseValidator:

    @abc.abstractmethod
    def validate(self, json):
        pass


class JSONValidator(BaseValidator):
    """Validator for json data

    Args:
        schema (dict): schema which describes what kind of json you expect
    """
    def __init__(self, schema):
        self._schema = schema

    def validate(self, json):
        try:
            validate(json, self._schema)
        except exceptions.ValidationError:
            return False
        return True
