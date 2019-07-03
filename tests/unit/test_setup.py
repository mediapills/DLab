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

from errno import ENOENT
import unittest
from mock import patch, mock_open, Mock

from dlab_core.setup import Director, DLabSetupException, ParametersBuilder

LIB_NAME = 'dlab_core.setup.'

FN_OPEN = LIB_NAME + 'open'
FN_FIND_PACKAGES = LIB_NAME + 'find_packages'
FN_ISFILE = LIB_NAME + 'os.path.isfile'
LIB_NAME_PATH = LIB_NAME + 'os.path'
LIB_NAME_SYS = LIB_NAME + 'sys'
SYS_PLATFORM = LIB_NAME_SYS + '.platform'

MOCK_NAME = 'dlab_core'
MOCK_DESCRIPTION_SHORT = 'Test short description ...'


def mock_isfile(result=True):

    def decorator(func):

        def wrapper(*args):
            with patch(FN_ISFILE, return_value=result):
                return func(*args)

        return wrapper

    return decorator


def mock_sys_platform(result='linux2'):
    def decorator(func):

        def wrapper(*args):
            with patch(SYS_PLATFORM, return_value=result):
                return func(*args)

        return wrapper

    return decorator


class TestParametersBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = ParametersBuilder(
            MOCK_NAME,
            MOCK_DESCRIPTION_SHORT
        )

    def test_constructor(self):
        params = self.builder.parameters

        self.assertEqual(params['name'], MOCK_NAME)
        self.assertEqual(params['description'], MOCK_DESCRIPTION_SHORT)

    @patch(FN_FIND_PACKAGES, Mock(return_value=['foo', 'bar', 'baz']))
    def test_set_packages(self):
        self.builder.set_packages()
        params = self.builder.parameters

        self.assertEqual(params['packages'], ['foo', 'bar', 'baz'])

    @patch(FN_OPEN, mock_open(read_data="foo==1.0.0\nbar>=0.0.0\nbaz"))
    @mock_sys_platform()
    @mock_isfile()
    def test_set_requirements(self):
        self.builder.set_requirements()
        params = self.builder.parameters

        self.assertEqual(params['install_requires'], [
            'foo==1.0.0',
            'bar>=0.0.0',
            'baz'
        ])

    @mock_isfile(False)
    def test_no_requirements_file(self):
        with self.assertRaises(DLabSetupException):
            self.builder.set_requirements()

    @mock_isfile()
    @patch(FN_OPEN, mock_open(read_data=''))
    def test_set_requirements_for_win(self):
        with patch(LIB_NAME_SYS) as mock:
            mock.platform = 'win32'

            self.builder.set_requirements()
            requires = self.builder.parameters['install_requires']

            self.assertGreater(len(requires), 0)

    @patch(FN_OPEN, Mock(side_effect=IOError(
        ENOENT,
        "No such file or directory",
        'some_file.txt'
    )))
    @mock_isfile()
    def test_set_requirements_file_read_error(self):
        with self.assertRaises(DLabSetupException):
            self.builder.set_requirements()

    @patch(FN_OPEN, mock_open(read_data='__version__ = "0.0.1"'))
    def test_set_lib_version(self):
        with patch(LIB_NAME_PATH) as mock:
            mock.isfile = lambda path: path == self.builder.lib_file

            self.builder.set_version()
            params = self.builder.parameters

            self.assertEqual(params['version'], '0.0.1')

    @patch(FN_OPEN, mock_open(read_data='__version__ = "0.0.1"'))
    def test_set_file_version(self):
        with patch(LIB_NAME_PATH) as mock:
            mock.isfile = lambda path: path == self.builder.version_file

            self.builder.set_version()
            params = self.builder.parameters

            self.assertEqual(params['version'], '0.0.1')

    @mock_isfile(False)
    def test_no_version_file(self):
        with self.assertRaises(DLabSetupException):
            self.builder.set_version()

    @mock_isfile()
    @patch(FN_OPEN, Mock(side_effect=IOError(
        ENOENT,
        "No such file or directory",
        'some_file.txt'
    )))
    def test_version_file_read_error(self):
        with self.assertRaises(DLabSetupException):
            self.builder.set_version()

    @patch(FN_OPEN, mock_open(read_data=''))
    @mock_isfile()
    def test_no_version_var(self):
        with self.assertRaises(DLabSetupException):
            self.builder.set_version()

    @patch(FN_OPEN, mock_open(read_data='file content'))
    @mock_isfile()
    def test_version_not_exec_content(self):
        with self.assertRaises(DLabSetupException):
            self.builder.set_version()

    @patch(FN_OPEN, mock_open(read_data='Long description ...'))
    @mock_isfile()
    def test_set_long_description(self):
        self.builder.set_long_description()
        params = self.builder.parameters

        self.assertEqual(params['long_description'], 'Long description ...')

    @mock_isfile(False)
    def test_no_long_description_file(self):
        with self.assertRaises(DLabSetupException):
            self.builder.set_long_description()


class TestDirector(unittest.TestCase):

    REQUIRED = {'version',
                'description',
                'author',
                'author_email',
                'url',
                'packages'}

    class ParametersBuilderA(ParametersBuilder):
        def set_requirements(self):
            self._parameters['install_requires'] = 'foo>=0.0.0'

        def set_version(self):
            self._parameters['version'] = '0.0.0'

        def set_long_description(self):
            self._parameters['long_description'] = 'Some text'

    def test_parameters(self):
        self._director = Director()
        builder = self.ParametersBuilderA(MOCK_NAME, MOCK_DESCRIPTION_SHORT)
        self._director.build(builder)
        parameters = self._director.parameters  # type: dict

        self.assertTrue(self.REQUIRED.issubset(parameters.keys()))
        self.assertEqual(builder.name, MOCK_NAME)
