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

import json

import os
import re
import requests
from deepdiff import DeepDiff
from radish import given, when, then, world

http_headers_to_send = dict()


def set_http_headers(step, headers):
    """
    Saves the HTTP request headers so they can be used in the next request.

    :param step: the test step context data.
    :param headers: the HTTP headers to use in the next request.
    """

    global http_headers_to_send

    http_headers_to_send = dict(headers)


def set_http_response(step, r):
    """
    Saves the HTTP response from a given request in the test step context for later retrieval where applicable.

    :param step: the test step context data.
    :param r: the Response object from the HTTP request.
    :return: The response (to the HTTP request done) status code and JSON data as test step context data.
    """

    step.context.api = dict()
    step.context.api['response'] = dict()
    step.context.api['response']['status'] = r.status_code
    step.context.api['response']['text'] = r.text

    try:
        step.context.api['response']['json'] = r.json()
    except ValueError:
        # No JSON no problem, should be by design.
        pass

    # Clears any existing HTTP request headers to prevent poisoning the next request.
    global http_headers_to_send
    http_headers_to_send = dict()


def http_get(step, url):
    r = requests.get(url, headers=http_headers_to_send)
    set_http_response(step, r)


def http_post(step, url, data):
    r = requests.post(url, headers=http_headers_to_send, data=data)
    set_http_response(step, r)


def http_post_json(step, url, data):
    r = requests.post(url, headers=http_headers_to_send, json=data)
    set_http_response(step, r)


def http_post_file(step, url, files):
    r = requests.post(url, headers=http_headers_to_send, files=files)
    set_http_response(step, r)


def http_patch_json(step, url, data):
    r = requests.patch(url, headers=http_headers_to_send, json=data)
    set_http_response(step, r)


def http_delete(step, url, headers):
    r = requests.delete(url, headers=headers)
    set_http_response(step, r)


def matches_json_file(step, file):
    """
    Checks whether the JSON response from a request matches the expected data present in a file. Any mismatch
    information is provided in the form of an assertion stating the differences.

    :param step: the test step context data
    :param file: the file where the expected data lives. It is assumed that the file base path is the expected output
    folder defined in the testing environment settings.
    """

    with open(os.path.join(world.env['data']['expected_output'], file), 'r') as file_contents:
        expected_info = json.loads(file_contents.read())

    actual_data = dict()
    if 'json' in step.context.api['response']:
        actual_data = step.context.api['response']['json']

    matches_json(actual_data, expected_info)


def matches_json(actual_data, expected_info):
    """
    Checks whether the JSON response from a request matches the expected data present in a file. Any mismatch
    information is provided in the form of an assertion stating the differences.

    The JSON data comparison doesn't care for the keys order. As long as it is present, no matter the insertion order,
    the comparison is properly ensured only raising issues if the actual contents differ.

    The expected data may have special "commands" to state what to ignore from the expected data. The logic starts off
    by assuming no such "commands" are present but if they are it operates accordingly. Any missing mandatory
    command raises a KeyError exception.

    The data to ignore for the comparison follows the deepdiff package definition (
    https://github.com/seperman/deepdiff#exclude-types-or-paths).

    :param actual_data: the data to check for matchness.
    :param expected_info: the expected data, including the special "commands".
    """

    # Determine what to validate.
    expected_data = expected_info
    ignore = set()
    if 'ignore' in expected_info:
        # 'ignore' always precedes expected data, otherwise the schema is wrong.
        if 'expected' not in expected_info:
            raise KeyError(
                "Expected data schema missing 'expected' key in: " + expected_info)

        expected_data = expected_info['expected']
        ignore = expected_info['ignore']

    # TODO this should use 'ignore_order=True' but it doesn't work.
    # This should cater for out-of-order keys in a response (i.e., key exists and value matches but isn't in the
    # order it's expected). However the feature isn't available at the time of writing this code due to 'Comparing
    # similar objects when ignoring order' (https://github.com/seperman/deepdiff/issues/29).
    diffs = DeepDiff(actual_data, expected_data, exclude_paths=ignore)
    assert diffs == {}, diffs


@then(re.compile(u'I expect the JSON response to be as in (.*)'))
def expected_result_as_file_json(step, file):
    matches_json_file(step, file)


@when(u'I list the backend API endpoints')
def list_endpoints(step):
    http_get(step, world.env['hosts']['backend_api']['host'])


@then(u'I expect the response code {:d}')
def expected_status_code(step, code):
    """
    Checks whether the status code returned from a previous HTTP request is as expected.

    The status code comes from the test step context data.

    :param step: the test step context data
    :param code: the expected HTTP status code
    """
    assert step.context.api['response']['status'] == code, 'status code: {}\n and message: {}'.format(str(
        step.context.api['response']['status']), step.context.api['response']['text'])


@given(re.compile(u'I mock the vNSFO response with (.*)'))
def set_vnsfo_mock_response(step, file):
    """
    Defines the response to be sent by the mock vNSF Orchestrator.

    :param step: the test step context data
    :param file: the file where the mock data lives. It is assumed that the file base path is the mock-vNSFO-data
    folder defined in the testing environment settings.
    """

    step.context.mock_vnsfo['response_file'] = file
