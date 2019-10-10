import json
import os
import sys


class CommandBuilder(object):
    param_string = "--{}={}"

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def params(self):
        request_data = json.loads(self.request)

        return ' '.join(
            [
                self.param_string.format(key.replace('-', '_'), val)
                for key, val in request_data.items()
            ]
        )

    @property
    def __executable_path(self):
        return os.path.dirname(sys.executable)

    @property
    def dlab(self):
        return os.path.join(self.__executable_path, 'dlab')

    @property
    def python(self):
        return os.path.join(self.__executable_path, 'python')

    def build_cmd(self):
        return [self.python, self.dlab, self.resource, self.action, self.params]