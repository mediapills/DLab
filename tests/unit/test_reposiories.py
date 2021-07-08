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
import argparse
import os
import sys
import six
import unittest

from dlab_core.infrastructure import repositories
from dlab_core.infrastructure import repositories as exceptions
from mock import patch

from api.models import FIFOModel, DlabModel


def mock_config_parser(data):

    def decorator(func):

        def wrapper(*args):
            parser = '.'.join([
                repositories.ConfigParser.__module__,
                repositories.ConfigParser.__name__
            ])

            with patch(parser + '.sections', return_value=data['s']):
                with patch(parser + '.options', return_value=data['k']):
                    with patch(parser + '.get', return_value=data['v']):
                        return func(*args)

        return wrapper

    return decorator


def mock_isfile_true(func):

    def wrapper(*args):
        with patch('os.path.isfile', return_value=True):
            return func(*args)

    return wrapper


@six.add_metaclass(abc.ABCMeta)
class BaseRepositoryTestCase:

    @abc.abstractmethod
    def test_find_one(self):
        pass

    @abc.abstractmethod
    def test_find_all(self):
        pass

    @abc.abstractmethod
    def test_find_one_wrong_key(self):
        pass

    @abc.abstractmethod
    def test_lower_case_sensitivity(self):
        pass

    @abc.abstractmethod
    def test_upper_case_sensitivity(self):
        pass


class TestArrayRepository(BaseRepositoryTestCase, unittest.TestCase):

    def setUp(self):
        self.repo = repositories.ArrayRepository()

    def test_constructor(self):
        repo = repositories.ArrayRepository({})
        self.assertEqual(repo.data, {})

    def test_constructor_validation(self):
        with self.assertRaises(exceptions.RepositoryDataTypeException):
            repositories.ArrayRepository('string')

    def test_find_one(self):
        self.repo.append('key', 'value')
        val = self.repo.find_one('key')

        self.assertEqual('value', val)

    def test_find_all(self):
        self.repo.append('key', 'value')
        data = self.repo.find_all()

        self.assertEqual({'key': 'value'}, data)

    def test_find_one_wrong_key(self):
        val = self.repo.find_one('wrong_key')

        self.assertIsNone(val)

    def test_lower_case_sensitivity(self):
        self.repo.append('lower_case_key', 'lower_case_value')
        val = self.repo.find_one('lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('LOWER_CASE_KEY'))

    def test_upper_case_sensitivity(self):
        self.repo.append('UPPER_CASE_KEY', 'upper_case_value')
        val = self.repo.find_one('UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(self.repo.find_one('upper_case_key'))

    def test_append(self):
        self.repo.append('key', 'value')
        self.repo.append('other_key', 'other_value')
        val = self.repo.find_one('other_key')

        self.assertEqual('other_value', val)

    def test_replace(self):
        self.repo.append('key', 'value')
        self.repo.append('key', 'other_value')
        val = self.repo.find_one('key')

        self.assertEqual('other_value', val)


class TestEnvironRepository(BaseRepositoryTestCase, unittest.TestCase):
    MOCK_ENVIRON = {'key': 'value'}
    MOCK_ENVIRON_LOWER_CASE = {'lower_case_key': 'lower_case_value'}
    MOCK_ENVIRON_UPPER_CASE = {'UPPER_CASE_KEY': 'upper_case_value'}

    @patch.dict('os.environ', MOCK_ENVIRON)
    def test_find_one(self):
        self.repo = repositories.EnvironRepository()
        val = self.repo.find_one('key')

        self.assertEqual('value', val)

    @patch.dict('os.environ', MOCK_ENVIRON)
    def test_find_all(self):
        self.repo = repositories.EnvironRepository()
        data = self.repo.find_all()
        key = 'key'
        # TODO must work in library not tests (move this if in lib)
        if sys.platform == 'win32':
            key = 'KEY'

        self.assertIn(key, data)

    def test_find_one_wrong_key(self):
        self.repo = repositories.EnvironRepository()
        val = self.repo.find_one('wrong_key')

        self.assertIsNone(val)

    # TODO check if sys.platform can help here for win
    @unittest.skipIf(sys.platform == 'win32', reason="does not run on windows")
    @patch.dict('os.environ', MOCK_ENVIRON_LOWER_CASE)
    def test_lower_case_sensitivity(self):
        self.repo = repositories.EnvironRepository()
        val = self.repo.find_one('lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('LOWER_CASE_KEY'))

    # TODO check if sys.platform can help here for win
    @unittest.skipIf(sys.platform == 'win32', reason="does not run on windows")
    @patch.dict('os.environ', MOCK_ENVIRON_UPPER_CASE)
    def test_upper_case_sensitivity(self):
        self.repo = repositories.EnvironRepository()
        val = self.repo.find_one('UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(self.repo.find_one('upper_case_key'))


class TestJSONContentRepository(BaseRepositoryTestCase, unittest.TestCase):
    MOCK_CONTENT = '{"key": "value"}'
    MOCK_CONTENT_LOWER_CASE = '{"lower_case_key": "lower_case_value"}'
    MOCK_CONTENT_UPPER_CASE = '{"UPPER_CASE_KEY": "upper_case_value"}'

    def test_constructor(self):
        repo = repositories.JSONContentRepository(self.MOCK_CONTENT)

        self.assertEqual(repo.content, self.MOCK_CONTENT)

    def test_constructor_validation(self):
        with self.assertRaises(exceptions.RepositoryDataTypeException):
            repositories.JSONContentRepository({})

    def test_find_one(self):
        repo = repositories.JSONContentRepository(self.MOCK_CONTENT)
        val = repo.find_one('key')

        self.assertEqual('value', val)

    def test_find_all(self):
        repo = repositories.JSONContentRepository(self.MOCK_CONTENT)
        data = repo.find_all()

        self.assertEqual({'key': 'value'}, data)

    def test_find_one_wrong_key(self):
        repo = repositories.JSONContentRepository(self.MOCK_CONTENT)
        val = repo.find_one('wrong_key')

        self.assertIsNone(val)

    def test_lower_case_sensitivity(self):
        repo = repositories.JSONContentRepository(
            self.MOCK_CONTENT_LOWER_CASE
        )
        val = repo.find_one('lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(repo.find_one('LOWER_CASE_KEY'))

    def test_upper_case_sensitivity(self):
        repo = repositories.JSONContentRepository(
            self.MOCK_CONTENT_UPPER_CASE
        )
        val = repo.find_one('UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(repo.find_one('upper_case_key'))

    def test_reload_content(self):
        repo = repositories.JSONContentRepository(self.MOCK_CONTENT)
        repo.content = '{"new_key": "new_value"}'
        data = repo.find_all()

        self.assertEqual({'new_key': 'new_value'}, data)

    def test_no_json_object(self):
        with self.assertRaises(exceptions.RepositoryJSONContentException):
            repositories.JSONContentRepository('not_json_content')


class TestArgumentsRepository(BaseRepositoryTestCase, unittest.TestCase):
    MOCK_ARGS = [
        'unittest_runner.py',
        '--key', 'value',
    ]

    MOCK_ARGS_LOWER_CASE = [
        'unittest_runner.py',
        '--lower_case_key', 'lower_case_value',
    ]

    MOCK_ARGS_UPPER_CASE = [
        'unittest_runner.py',
        '--UPPER_CASE_KEY', 'upper_case_value',
    ]

    def setUp(self):
        self.repo = repositories.ArgumentsRepository()

    def test_constructor(self):
        parser = argparse.ArgumentParser()
        repo = repositories.ArgumentsRepository(parser)

        self.assertEqual(repo.arg_parse, parser)

    def test_constructor_validation(self):
        with self.assertRaises(exceptions.RepositoryDataTypeException):
            repositories.ArgumentsRepository('string')

    @patch('sys.argv', MOCK_ARGS)
    def test_find_one(self):
        self.repo.add_argument('--key')
        val = self.repo.find_one('key')

        self.assertEqual('value', val)

    @patch('sys.argv', MOCK_ARGS)
    def test_find_all(self):
        self.repo.add_argument('--key')
        data = self.repo.find_all()

        self.assertEqual({'key': 'value'}, data)

    @patch('sys.argv', MOCK_ARGS)
    def test_find_one_wrong_key(self):
        with self.assertRaises(exceptions.RepositoryWrongArgumentException):
            val = self.repo.find_one('wrong_key')
            self.assertIsNone(val)

    @patch('sys.argv', MOCK_ARGS_LOWER_CASE)
    def test_lower_case_sensitivity(self):
        self.repo.add_argument('--lower_case_key')
        val = self.repo.find_one('lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('LOWER_CASE_KEY'))

    @patch('sys.argv', MOCK_ARGS_UPPER_CASE)
    def test_upper_case_sensitivity(self):
        self.repo.add_argument('--UPPER_CASE_KEY')
        val = self.repo.find_one('UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(self.repo.find_one('upper_case_key'))

    def test_unrecognized_arguments(self):
        sys.argv.append('argument')

        with self.assertRaises(exceptions.RepositoryWrongArgumentException):
            self.repo.find_one('option')


class TestConfigRepository(BaseRepositoryTestCase, unittest.TestCase):
    MOCK_FILE_PATH = '/test.ini'

    MOCK_CONFIG = {
        's': ['section'],
        'k': ['key'],
        'v': 'value',
    }
    MOCK_CONFIG_LOWER_CASE = {
        's': ['section'],
        'k': ['lower_case_key'],
        'v': 'lower_case_value',
    }
    MOCK_CONFIG_UPPER_CASE = {
        's': ['SECTION'],
        'k': ['UPPER_CASE_KEY'],
        'v': 'upper_case_value',
    }

    @mock_isfile_true
    def setUp(self):
        self.repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)

    @mock_config_parser(data=MOCK_CONFIG)
    def test_find_one(self):
        val = self.repo.find_one('section_key')

        self.assertEqual('value', val)

    @mock_config_parser(data=MOCK_CONFIG)
    def test_find_all(self):
        data = self.repo.find_all()
        self.assertEqual({'section_key': 'value'}, data)

    @mock_config_parser(data=MOCK_CONFIG)
    def test_find_one_wrong_key(self):
        val = self.repo.find_one('wrong_key')

        self.assertIsNone(val)

    def test_file_not_exist(self):
        location = 'new_test.ini'

        with self.assertRaises(exceptions.RepositoryFileNotFoundException):
            self.repo.location = location

    @mock_isfile_true
    def test_change_file(self):
        location = 'new_test.ini'
        self.repo.location = location

        self.assertEqual(location, self.repo.location)

    @mock_config_parser(data=MOCK_CONFIG_LOWER_CASE)
    def test_lower_case_sensitivity(self):
        val = self.repo.find_one('section_lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('SECTION_LOWER_CASE_KEY'))

    @mock_config_parser(data=MOCK_CONFIG_UPPER_CASE)
    def test_upper_case_sensitivity(self):
        val = self.repo.find_one('SECTION_UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(self.repo.find_one('upper_case_key'))

    def test_constructor_exception(self):
        with self.assertRaises(exceptions.RepositoryDataTypeException):
            self.repo = repositories.ConfigRepository(None)

    @mock_isfile_true
    def test_location_exception(self):
        with self.assertRaises(exceptions.RepositoryDataTypeException):
            self.repo.location = None


class TestChainOfRepositories(BaseRepositoryTestCase, unittest.TestCase):

    def setUp(self):
        arr = repositories.ArrayRepository()
        arr.append('key', 'value')

        self.repo = repositories.ChainOfRepositories()
        self.repo.register(arr)

    def test_constructor(self):
        arr = repositories.ArrayRepository()
        repo = repositories.ChainOfRepositories([arr])

        self.assertEqual(repo._repos[0], arr)

    def test_constructor_validation(self):
        with self.assertRaises(exceptions.RepositoryDataTypeException):
            repositories.ChainOfRepositories('string')

    def test_find_one(self):
        val = self.repo.find_one('key')

        self.assertEqual('value', val)

    def test_find_all(self):
        data = self.repo.find_all()

        self.assertEqual({'key': 'value'}, data)

    def test_find_one_wrong_key(self):
        val = self.repo.find_one('wrong_key')

        self.assertIsNone(val)

    def test_lower_case_sensitivity(self):
        arr = repositories.ArrayRepository()
        arr.append('lower_case_key', 'lower_case_value')
        self.repo.register(arr)
        val = self.repo.find_one('lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('SECTION_LOWER_CASE_KEY'))

    def test_upper_case_sensitivity(self):
        arr = repositories.ArrayRepository()
        arr.append('SECTION_UPPER_CASE_KEY', 'upper_case_value')
        self.repo.register(arr)
        val = self.repo.find_one('SECTION_UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(self.repo.find_one('upper_case_key'))

    def test_register_validation(self):
        with self.assertRaises(exceptions.RepositoryDataTypeException):
            self.repo.register('str')


class TestSQLiteRepository(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.db_path = os.path.join(self.base_dir, '..', 'database')
        with patch('dlab_core.infrastructure.repositories.SQLiteRepository'):
            self.dbc = repositories.SQLiteRepository(self.db_path)

        self.entity = DlabModel(
            request='data', resource='resource',
            action='action', status=0)

    def test_init_repo(self):
        self.dbc._init()
        self.dbc._init.assert_called_with()

    def test_execute_get(self):
        self.dbc._execute_get.return_value = 1
        self.dbc._execute_get()
        self.dbc._execute_get.assert_called_with()

    def test_execute_set(self):
        self.dbc._execute_set.return_value = 1
        self.dbc._execute_set()
        self.dbc._execute_set.assert_called_with()

    def test_find_one(self):
        self.dbc.find_one.return_value = {'action': 'action'}
        self.assertEqual(self.dbc.find_one(b'action'), {'action': 'action'})

    def test_insert(self):
        self.dbc.insert.return_value = 1
        self.assertEqual(self.dbc.insert(self.entity), 1)
        self.dbc.insert.assert_called_with(self.entity)

    def test_update(self):
        self.dbc.update.return_value = 1
        self.assertEqual(self.dbc.update(self.entity), 1)
        self.dbc.update.assert_called_with(self.entity)

    def test_fields_list(self):
        self.dbc.fields_list.return_value = [
            'request', 'resource', 'action', 'status'
        ]
        self.assertEqual(
            self.dbc.fields_list(self.entity),
            ['request', 'resource', 'action', 'status']
        )
        self.dbc.fields_list.assert_called_with(self.entity)

    def test_fields(self):
        self.dbc.fields.return_value = 'request,resource,action,status'
        self.assertEqual(
            self.dbc.fields(self.entity),
            'request,resource,action,status'
        )
        self.dbc.fields.assert_called_with(self.entity)

    def test_values(self):
        self.dbc.values.return_value = ['data', 'resource', 'action', 0]
        self.assertEqual(
            self.dbc.values(self.entity),
            ['data', 'resource', 'action', 0]
        )
        self.dbc.values.assert_called_with(self.entity)

    def test_question_marks(self):
        self.dbc.question_marks.return_value = '?,?'
        self.assertEqual(
            self.dbc.question_marks(self.entity),
            '?,?'
        )
        self.dbc.question_marks.assert_called_with(self.entity)

    def test_prepare_update_data(self):
        self.dbc._prepare_update_data.return_value = 'param1, param2'
        self.assertEqual(
            self.dbc._prepare_update_data(self.entity),
            'param1, param2'
        )
        self.dbc._prepare_update_data.assert_called_with(self.entity)


class TestFIFOSQLiteQueueRepository(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.db_path = os.path.join(self.base_dir, '..', 'database')
        with patch(
            'dlab_core.infrastructure.repositories.FIFOSQLiteQueueRepository'
        ):
            self.dbc = repositories.FIFOSQLiteQueueRepository(self.db_path)

        self.entity = FIFOModel(id=1)

    def test_insert(self):
        self.dbc.insert.return_value = None
        self.dbc.insert(self.entity)
        self.dbc.insert.assert_called_with(self.entity)

    def test_get(self):
        self.dbc.get.return_value = 1
        self.dbc.get(self.entity)
        self.dbc.get.assert_called_with(self.entity)

    def test_delete(self):
        self.dbc.delete.return_value = None
        self.dbc.delete(self.entity)
        self.dbc.delete.assert_called_with(self.entity)
