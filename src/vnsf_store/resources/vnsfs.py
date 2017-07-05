from flask_restful import Resource
from flask_restful_swagger_2 import swagger

import endpoints_base
from common import constants as const


class Vnsf(Resource):
    """
    vNSF onboarding endpoints
    """

    @swagger.doc({
        'consumes': ['multipart/form-data'],
        'produces': const.API_RESPONSE_TYPE,
        'summary': 'Triggers the vNSF onboarding process',
        'description': '''
Due to the nature of the process, as it comprises time-consuming operations such as validations and 
considerable-sized downloads, the submission request is promptly acknowledged and the process continues in the 
background. Later on, the caller will be notified whether the operation succeeded or failed.<br /><br />To ensure 
a vNSF can be onboarded, the descriptors provided in the package need to be validated. These descriptors are checked 
for:</p>
<ul>
<li>Syntax errors to prevent incorrect vNSF descriptors from being processed.</li>
<li>vNSF topology integrity to avoid potential loops or errors such as references to undefined network 
interfaces.</li>
</ul>
<p>Every onboarded vNSF descriptor will be checked for syntax, correctness and completeness issues. With no issues 
found the next step is to check the defined network topology and ensure inconsistencies such as no unconnected 
interfaces are present and all virtual links are properly defined. Upon successful validation, the vNSF may proceed 
with the onboarding process. Any error results in a notification to the Developer stating what is not
compliant with the SHIELD requirements.</p>
            ''',
        'tags': [endpoints_base.ENDPOINT_VNSFS],
        'parameters': [
            {
                'name': 'vnsf_package',
                'description': 'The vNSF package file to onboard',
                'required': True,
                'in': 'formData',
                'type': 'file'
            }
        ],
        'responses': const.swagger_api_custom_response({
            str(const.HTTP_202_ACCEPTED):
                {
                    'description': 'vNSF onboarding request registered. Operation status will be deferred in time.',
                }})
    })
    def post(self):
        return '', const.HTTP_501_NOT_IMPLEMENTED
