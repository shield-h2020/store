import copy

JSON_UTF8_RESPONSE_TYPE = 'application/json; charset=utf-8'

API_RESPONSE_TYPE = [JSON_UTF8_RESPONSE_TYPE]

# Redefine HTTP codes as they seem to no longer be available at Flask (it was on flask.ext.api but it doesn't seem to be
# ported).
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_203_NON_AUTHORITATIVE_INFORMATION = 203
HTTP_204_NO_CONTENT = 204
HTTP_205_RESET_CONTENT = 205
HTTP_206_PARTIAL_CONTENT = 206

HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_402_PAYMENT_REQUIRED = 402
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_406_NOT_ACCEPTABLE = 406
HTTP_407_PROXY_AUTHENTICATION_REQUIRED = 407
HTTP_408_REQUEST_TIMEOUT = 408
HTTP_409_CONFLICT = 409
HTTP_410_GONE = 410
HTTP_411_LENGTH_REQUIRED = 411
HTTP_412_PRECONDITION_FAILED = 412
HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_414_REQUEST_URI_TOO_LONG = 414
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
HTTP_417_EXPECTATION_FAILED = 417
HTTP_428_PRECONDITION_REQUIRED = 428
HTTP_429_TOO_MANY_REQUESTS = 429
HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431

HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_501_NOT_IMPLEMENTED = 501
HTTP_502_BAD_GATEWAY = 502
HTTP_503_SERVICE_UNAVAILABLE = 503
HTTP_504_GATEWAY_TIMEOUT = 504
HTTP_505_HTTP_VERSION_NOT_SUPPORTED = 505
HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = 511

"""
HTTP API response template. This will be tailored for each response. 
"""
HTTP_RESPONSE = {
    str(HTTP_200_OK): {"description": "Request succeeded."},

    str(HTTP_202_ACCEPTED): {
        "description": "Request processing. You can retry your request, and when it's complete, you'll get a 200 "
                       "instead."},

    str(HTTP_400_BAD_REQUEST): {"description": "Bad request. API specific parameters are incorrect or missing."},

    str(HTTP_401_UNAUTHORIZED): {"description": "Unauthorised. You're not authorised to access this resource."},

    str(HTTP_404_NOT_FOUND): {"description": "Not found. The requested resource doesn't exist."},

    str(HTTP_500_INTERNAL_SERVER_ERROR): {"description": "Server errors. Our bad!"},

    str(HTTP_501_NOT_IMPLEMENTED): {"description": "Not implemented yet."},

    str(HTTP_504_GATEWAY_TIMEOUT): {
        "description": "Timeout. A request to a third-party has taken too long to ve served."}
}


def swagger_api_custom_response(modified_codes, remove_codes=None):
    """
    Takes the API response template and updates the intended code with the desired details.

    :param modified_codes: The HTTP codes (along with the data) to update in the template response
    :param remove_codes: The HTTP codes to remove from the response, if applicable
    :return: The swagger response entry with the common template updated with the intended response for the desired
    HTTP code.
    """

    api_responses = copy.deepcopy(HTTP_RESPONSE)

    for code, new_data in modified_codes.items():
        api_responses[str(code)] = new_data

    return swagger_api_custom_response_remove(api_responses, remove_codes)


def swagger_api_custom_response_remove(http_codes, remove_codes=None):
    """
    Takes the API response template and removes the intended code(s).

    :param http_codes: The set of HTTP codes to remove elements from
    :param remove_codes: The HTTP codes to remove from the http_codes, if applicable
    :return: The swagger response entry without the intended codes HTTP code.
    """

    if remove_codes is None:
        return http_codes

    for code in remove_codes:
        http_codes.pop(str(code), None)

    return http_codes
