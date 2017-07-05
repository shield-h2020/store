from flask_restful import Resource
from flask_restful_swagger_2 import swagger

import endpoints_base
from common import constants as const
from model import vnsf_model


class VnsfElement(Resource):
    """
    vNSF element endpoints
    """

    @swagger.doc({
        'produces': const.API_RESPONSE_TYPE,
        'summary': 'Details on an onboarded vNSF',
        'description': 'Provides information on the onboarded vNSF.',
        'tags': [endpoints_base.ENDPOINT_VNSFS],
        'parameters': [
            {
                'name': 'vnsf_id',
                'description': 'The vNSF identifier',
                'required': True,
                'in': 'path',
                'type': 'integer',
            }
        ],
        'responses': const.swagger_api_custom_response({
            str(const.HTTP_200_OK):
                {
                    'description': 'Onboarded vNSF details.',
                    'schema': vnsf_model.VnsfDetails,
                    'examples': {
                        const.JSON_UTF8_RESPONSE_TYPE: {
                            'TBD': 0
                        }
                    }
                }})
    })
    def get(self, vnsf_id):
        return '', const.HTTP_501_NOT_IMPLEMENTED

    @swagger.doc({
        'produces': const.API_RESPONSE_TYPE,
        'summary': 'Decommissions an onboarded vNSF',
        'description': '''
Takes a vNSF of service and prevents it from ever being instantiated again. For a running vNSF a graceful 
decommission is provided by scheduling of the operation to a later date.
''',
        'tags': [endpoints_base.ENDPOINT_VNSFS],
        'parameters': [
            {
                'name': 'vnsf_id',
                'description': 'The vNSF identifier',
                'required': True,
                'in': 'path',
                'type': 'integer',
            }
        ],
        'responses': const.swagger_api_custom_response({
            str(const.HTTP_200_OK):
                {
                    'description': 'vNSF decommissioned.'
                },
            str(const.HTTP_202_ACCEPTED):
                {
                    'description': 'vNSF in use. It will be decommissioned at a later stage.'
                }},
                [const.HTTP_201_CREATED])
    })
    def delete(self, vnsf_id):
        return '', const.HTTP_501_NOT_IMPLEMENTED
