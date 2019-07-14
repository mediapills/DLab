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

from dlab_core.domain.exceptions import DLabException


class FrozenServiceException(DLabException):
    """Raised when try to access a key that is represent frozen data in
    a dictionary (dict).
    """

    def __init__(self, key):
        super(FrozenServiceException, self).__init__(
            'Cannot override frozen service "{}".'.format(key)
        )


class KeyException(KeyError):
    """Raised when try to access a key that isn't in a dictionary (dict).
    """

    def __init__(self, key):
        super(KeyException, self).__init__(key)


class ExpectedCallableException(DLabException):
    pass


# TODO implement all magic methods
class Container:
    """Instantiates the container.
    Objects and parameters can be passed as argument to the constructor.

    :type args: dict
    :param args: The parameters or objects.
    """

    def __init__(self, args=None):
        self._data = {}
        self._frozen = set()
        self._raw = {}
        self._protected = set()

        if args is None:
            args = {}
        elif not isinstance(args, dict):
            raise TypeError(type(args))

        for key in args.keys():
            self[key] = args[key]

    def __setitem__(self, key, value):
        """Sets a parameter or an object. Objects must be defined as Closures.
        Allowing any python callable leads to difficult to debug problems as
        function names (strings) are callable (creating a function with the
        same name as an existing parameter would break your container).

        :param key: The unique identifier for the parameter or object.

        :param value: The value or a closure of the parameter.

        :raise FrozenServiceException: Prevent override of a frozen service.
        """

        if key in self._frozen:
            raise FrozenServiceException(key)

        self._data[key] = value

    def __getitem__(self, key):
        """Gets a parameter or an object.

        :type key: string
        :param key: The unique identifier for the parameter or object.

        :return: The value of the parameter or an object.

        :raise KeyException: When try to access a key that isn't in a dict.
        """

        if key not in self._data:
            raise KeyException(key)

        raw = self._data[key]

        if any([
            not callable(raw),
            key in self._frozen,
            raw in self._raw,
            raw in self._protected,
        ]):
            return raw

        self._raw[key] = raw
        self._frozen.add(key)

        val = self._data[key] = raw(self)

        return val

    def keys(self):
        """Return set-like object providing a view on container keys.

        :rtype: set
        :return: Container keys.
        """

        return self._data.keys()

    def __len__(self):
        """Count elements of an object.

        :rtype: int
        :return The custom count as an integer.
        """

        return len(self._data)

    def __delitem__(self, key):
        """Unset element from container

        :type key: string
        :param key: The unique identifier for the parameter or object.

        :raise KeyException: When try to access a key that isn't in a dict.
        """

        if key not in self._data.keys():
            raise KeyException(key)

        raw = self._data[key]
        del self._data[key]

        if key in self._frozen:
            self._frozen.remove(key)

        if key in self._raw:
            del self._raw[key]

        if raw in self._protected:
            self._protected.remove(raw)

    def __repr__(self):
        """returns the object representation.

        :rtype: str
        :return: Object representation.
        """

        return repr({
            'data': self._data,
            'frozen': self._frozen,
            'raw': self._raw,
            'protected': self._protected
        })

    def clear(self):
        """Remove all items from container.
        """

        self._data.clear()
        self._frozen.clear()
        self._raw.clear()
        self._protected.clear()
        # self._factories.clear()

    def __iter__(self):
        """Get an iterator from an Container object.

        :rtype: iterator
        :return: Iterator object that loops through each element in the object.
        """

        return iter(self._data)

    def raw(self, key):
        """Gets a parameter or the closure defining an object.

        :type key: string
        :param key: The unique identifier for the parameter or object.

        :return: The value of the parameter or the closure defining an object:

        :raise: UnknownIdentifierException
        """

        if key not in self._data.keys():
            raise KeyException(key)

        if key in self._raw:
            return self._raw[key]

        return self._data[key]

    def protect(self, func):
        """Protects a callable from being interpreted as a service. This is
        useful when you want to store a callable as a parameter.

        :type func: function
        :param func: A callable to protect from being evaluated.

        :rtype: func
        :return: The passed callable.

        :raise: ExpectedCallableException
        """

        if not callable(func):
            raise ExpectedCallableException(func)

        self._protected.add(func)

        return func

    def factory(self, func):
        """Marks a callable as being a factory service.

        :type func: function
        :param func: A service definition to be used as a factory.

        :rtype function
        :return: The passed callable

        :raise: ExpectedCallableException
        """

        raise NotImplementedError

    def extend(self, key, func):
        """Extends an object definition. Useful when you want to extend an
        existing object definition, without necessarily loading that object.

        :type key: string
        :param key: The unique identifier for the parameter or object.

        :rtype: func
        :return: The passed callable.

        :rtype: function
        :return The wrapped callable.

        :raise: UnknownIdentifierException
        :raise: FrozenServiceException
        :raise: InvalidServiceIdentifierException
        :raise: ExpectedCallableException
        """

        raise NotImplementedError