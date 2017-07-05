from flask_restful_swagger_2 import Schema


class VduDetails(Schema):
    type = 'object'
    properties = {
        'image': {
            'type': 'string',
            'description': 'The path to the vNSF image file'},
        'hash': {
            'type': 'string',
            'description': 'The image file hash'}
    }

    required = list(properties.keys())


class VnsfManifest(Schema):
    type = 'object'
    properties = {
        'vdus': VduDetails.array()
    }

    required = list(properties.keys())


class VnsfDetails(Schema):
    type = 'object'
    properties = {
        'version': {
            'type': 'string',
            'description': 'The vNSF version'},
        'manifest': VnsfManifest
    }

    required = list(properties.keys())
