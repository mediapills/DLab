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

from setuptools import setup
from dlab_core.setup import SetupParametersDirector, SetupParametersBuilder


def do_setup():
    description = 'This a provider to DLab that adds GCP support.'

    builder = SetupParametersBuilder(
        'dlab_gcp',
        description
    )
    builder.set_entry_points({
        "dlab.plugin": [
            "gcp = dlab_gcp.registry:bootstrap",
        ],
    })
    director = SetupParametersDirector()
    director.build(builder)
    args = director.parameters

    setup(**args)


if __name__ == "__main__":
    do_setup()
