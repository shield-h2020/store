# -*- coding: utf-8 -*-
import json

import os
import re
import requests
from dictdiffer import diff
from radish import before, given, when, then, world
from shutil import rmtree, copyfile

http_headers_to_send = dict()


@before.each_scenario
def setup_scenario(step):
    # Avoid poisoning mocked responses for the vNSFO.
    if os.path.exists(world.env['mock-vnsfo-folder']):
        rmtree(world.env['mock-vnsfo-folder'])

    # Mock vNSFO context.
    step.context.mock_vnsfo = dict()

    # API context.
    step.context.api = dict()
    step.context.api['response'] = dict()


def ordered(obj):
    """
    Shallow-sorts a list or dictionary in ascending order.

    :param obj: the object to be sorted.
    :return: the sorted object.
    """
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def ordered_json(obj):
    """
    Shallow-sorts JSON data in ascending order.

    :param obj: the JSON data to sort.
    :return: the ordered data.
    """
    return dict(ordered(obj))


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


def http_post_file(step, url, files):
    r = requests.post(url, files=files)
    set_http_response(step, r)


def http_delete(step, url, headers):
    r = requests.delete(url, headers=headers)
    set_http_response(step, r)


def matches_file_json(step, file):
    """
    Checks whether the JSON response from a request matches the expected data present in a file. Any mismatch
    information is provided in the form of an assertion stating the differences.

    The JSON data comparison doesn't care for the keys order. As long as it is present, no matter the insertion order,
    the comparison is properly ensured only raising issues if the actual contents differ.

    The expected data may have special "commands" to state what to ignore from the expected data. The code starts of
    by assuming no such "commands" are present but if they are it operates accordingly. Any missing mandatory
    command raises a KeyError exception.

    :param step: the test step context data
    :param file: the file where the expected data lives. It is assumed that the file base path is the expected output
    folder defined in the testing environment settings.
    """

    file_contents = open(os.path.join(world.env['expected_output'], file), 'r')
    expected_info = json.loads(file_contents.read())
    file_contents.close()

    # Determine what to validate.
    expected_data = expected_info
    ignore = set()
    if 'ignore' in expected_info:
        # 'ignore' always precedes expected data, otherwise the schema is wrong.
        if 'expected' not in expected_info:
            raise KeyError(
                    "Expected data schema missing 'expected' key in: " + os.path.join(world.env['expected_output'],
                                                                                      file))

        expected_data = expected_info['expected']
        ignore = expected_info['ignore']

    expected_data = ordered_json(expected_data)
    actual_data = dict()
    if 'json' in step.context.api['response']:
        actual_data = ordered_json(step.context.api['response']['json'])

    result = list(diff(actual_data, expected_data, ignore=ignore))
    assert result == [], result


@when(re.compile(u'I onboard a vNSF (.*)'))
def vnsf_onboard(step, package):
    # Set proper vNSFO response.
    dest_file = os.path.join(world.env['mock-vnsfo-folder'], 'any', 'any.post.json')
    dest_path = os.path.dirname(dest_file)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path, exist_ok=True)
    copyfile(os.path.join(world.env['mock-vnsfo-data'], step.context.mock_vnsfo['response_file']), dest_file)

    # Onboard vNSF with the Orchestrator.
    with open(os.path.join(world.env['input_data'], package), 'rb') as f:
        files = {'package': f}
        http_post_file(step, world.endpoints['vnsfs'], files)


@when(re.compile(u'I decommission a (.*)'))
def vnsf_decommission(step, vnsf):
    vnsf_onboard(step, vnsf)
    url = '{}/{}'.format(world.endpoints['vnsfs'], step.context.api['response']['json']['_id'])
    headers = {'If-Match': step.context.api['response']['json']['_etag']}
    http_delete(step, url, headers=headers)


@then(re.compile(u'I expect the JSON response to be as in (.*)'))
def expected_result_as_file_json(step, file):
    matches_file_json(step, file)


@when(u'I list the endpoints')
def list_endpoints(step):
    http_get(step, world.env['host'])


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
    Defines the headers to send to the mock vNSF Orchestrator.

    :param step: the test step context data
    :param file: the file where the mock data lives. It is assumed that the file base path is the mock-vNSFO-data
    folder defined in the testing environment settings.
    """

    step.context.mock_vnsfo['response_file'] = file
