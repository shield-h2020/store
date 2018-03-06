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


def build_url(server, port=None, basepath=None, protocol=None):
    """
    Build a URL given the parameters provided. Depending on the parameters it may just simply return a hostname/IP
    address or None.

    :param server: The server name or IP address.
    :param port: The port where the server is listening for requests.
    :param basepath: The base path where the "endpoints" are available.
    :param protocol: The protocol to use for communicating with the server and reach the "endpoints"
    :return: A full URL (depending on the parameters it may just simply return a hostname/IP address or None).
    """

    if server is None:
        return None

    host = server

    if port is not None:
        host += ':' + port

    if protocol is None:
        return host

    url = '{}://{}'.format(protocol, host)
    if basepath is not None and len(basepath) > 0:
        url = '{}/{}'.format(url, basepath)

    return url


def _without_keys(dict_data, keyz):
    """
    Removes elements from a (copy of a) dictionary.

    :param dict_data: the dictionary to remove entries from.
    :param keyz: the keys to remove from the dictionary.
    :return: a new dictionary withiout the intended keys.
    """

    cleaned_data = dict_data.copy()

    for key in keyz:
        cleaned_data.pop(key)

    return cleaned_data


def tailor_response(initial, changes, remove):
    """
    Takes an initial response data and modifies it by changing the intended keys and removing the unwanted ones.

    :param initial: the initial response dictionary.
    :param changes: the dictionary keys with the intended changes for the values.
    :param remove: the list of key to remove from the response.
    :return: the tailored response.
    """

    tailored = initial.copy()

    if changes is not None:
        tailored = {**tailored, **changes}

    return _without_keys(tailored, remove)


# HTTP status codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_404_NOT_FOUND = 404
HTTP_406_NOT_ACCEPTABLE = 406
HTTP_412_PRECONDITION_FAILED = 412
HTTP_500_SERVER_ERROR = 500
HTTP_501_NOT_IMPLEMENTED = 501
HTTP_502_BAD_GATEWAY = 502
HTTP_504_TIMEOUT = 504

responses_full = {
    str(HTTP_200_OK): {
        'description': 'Request succeeded.'
        },
    str(HTTP_201_CREATED): {
        'description': 'Resource created.'
        },
    str(HTTP_202_ACCEPTED): {
        'description': "Request processing. You can retry your request, and when it's finished, you'll get a 200 "
                       "instead."
        },
    str(HTTP_400_BAD_REQUEST): {
        'description': 'Bad request. API specific parameters are incorrect or missing.'
        },
    str(HTTP_401_UNAUTHORIZED): {
        'description': "Unauthorised. You're not authorised to access this resource."
        },
    str(HTTP_404_NOT_FOUND): {
        'description': "Not found. The requested resource doesn't exist."
        },
    str(HTTP_500_SERVER_ERROR): {
        'description': 'Server errors. Our bad!'
        },
    str(HTTP_501_NOT_IMPLEMENTED): {
        'description': 'Not implemented yet.'
        },
    str(HTTP_502_BAD_GATEWAY): {
        'description': 'Third-party unreachable.'
        },
    str(HTTP_504_TIMEOUT): {
        'description': 'Timeout. A request to a third-party has taken too long to be served.'
        }
    }

responses = _without_keys(responses_full, [str(HTTP_501_NOT_IMPLEMENTED)])
responses_created = _without_keys(responses, [str(HTTP_200_OK)])
responses_read = _without_keys(responses, [str(HTTP_201_CREATED)])
responses_updated = _without_keys(responses, [str(HTTP_201_CREATED)])
responses_deleted = _without_keys(responses, [str(HTTP_201_CREATED)])
responses_not_implemented = _without_keys(responses_full,
                                          [str(HTTP_200_OK),
                                           str(HTTP_201_CREATED),
                                           str(HTTP_202_ACCEPTED),
                                           str(HTTP_502_BAD_GATEWAY),
                                           str(HTTP_504_TIMEOUT)])
