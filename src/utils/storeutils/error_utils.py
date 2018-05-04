# -*- coding: utf-8 -*-

#  Copyright (c) 2017 SHIELD, UBIWHERE
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SHIELD, UBIWHERE nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# This work has been performed in the framework of the SHIELD project,
# funded by the European Commission under Grant number 700199 through the
# Horizon 2020 program. The authors would like to acknowledge the contributions
# of their colleagues of the SHIELD partner consortium (www.shield-h2020.eu).


import sys
import logging
from werkzeug.datastructures import ImmutableMultiDict

from enum import Enum


class ExceptionMessage_(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class IssueElement(Enum):
    # Standard error types.
    CRITICAL = logging.CRITICAL,
    FATAL = logging.FATAL,
    ERROR = logging.ERROR,
    WARNING = logging.WARNING,
    INFO = logging.INFO,
    DEBUG = logging.DEBUG,

    # Additional elements allowed.
    EXCEPTION = '_exception_'


class IssueHandling(object):
    """
    Provide a mechanism to simplify the error maintenance in the code.

    The key component for the programmer is the errors dictionary which must follow a simple schema to organize
    errors and exceptions to raise for any given situation. Any way this dictionary is built, the data to provide to
    the methods here must have as key a string from the ErrorElement enumeration and for value as described next.

    errors = {
        '<type>': {
            'sub-type': {
                ErrorElement.DEBUG.name: [<list of whatever messages to produce for debugging purposes>, <this list
                must use {} for data substitution>],
                ErrorElement.EXCEPTION.name: <ExceptionMessage instance with associated message to provide for the
                exception>
                }

    NOTE:
        - the [<type>][<sub-type>] organization is optional and any depth may be used.
        - only the required keys from ErrorElement should be used. Any key not defined will raise a KeyError so the
        programmer knows it's missing from the dictionary.
    """

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def log(self, level, error_data, params=None):
        if params is not None:
            for idx, msg in enumerate(error_data[level.name]):
                self.logger.log(level.value[0], msg.format(*params[idx]))
        else:
            self.logger.log(level.value[0], error_data[level.name][0])

    def raise_ex(self, level, error_data, params=None):
        self.log(level, error_data, params)
        raise type(error_data[IssueElement.EXCEPTION.name])(str(error_data[IssueElement.EXCEPTION.name]))

    def raise_ex_2(self, level, error_data, params=None, this_exception=None):
        self.log(level, error_data, params)
        exc = error_data[IssueElement.EXCEPTION.name]
        e = type(exc)(this_exception.message)
        e.data = {'validation': 'ola'}
        raise e
        #raise type(exc)(this_exception.message)

    def build_ex(self, level, error_data, params=None, message=None):
        self.log(level, error_data, params)
        e = type(error_data[IssueElement.EXCEPTION.name])()
        code = e.code
        rsp = {
            "_status": "ERR",
            "_error": {
                "code": code,
                "message": message,
            }
        }
        return rsp
