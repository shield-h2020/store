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


from storeutils import http_utils

swagger_info = {
    'title': 'Store API',
    'version': '0.1.0',
    'description': "This API onboards vNSFs and NSs in a secure and trusted way. The onboarding process will ensure "
                   "the provenance is from a trusted source and that the contents integrity can be assured. Once this "
                   "is achieved the security information is stored for safekeeping and provided upon request so other "
                   "components can check that the vNSF/NS has not been tampered with since it was "
                   "onboarded.\n\nAnother relevant feature provided by the Store is the verification done on the vNSF "
                   "and NS associated descriptors to ensure the instantiation process by an Orchestrator is performed "
                   "without hassle.\n\n_Please note that consumers are not allowed to edit (`PATCH`), update (`PUT`) "
                   "or delete (`DELETE`) a resource unless they provide an up-to-date `ETag` for the resource they "
                   "are attempting to modify. This value, taken from the details (`GET`) request, is mandatory and "
                   "should be provided in the `If-Match` header_.\n\nAPI version numbering as per http://semver.org/",
    'termsOfService': 'my terms of service',
    'contact': {
        'name': 'Filipe Ferreira',
        'url': 'https://github.com/betakoder'
        },
    'license': {
        'name': 'Apache License, Version 2.0',
        'url': 'http://www.apache.org/licenses/LICENSE-2.0',
        },
    'schemes': ['http', 'https'],
    }

paths = {
    '/vnsfs': {
        'post': {
            'summary': 'Triggers the vNSF onboarding process',
            'description': "Due to the nature of the process, as it comprises time-consuming operations such as "
                           "validations and considerable-sized downloads, the submission request is promptly "
                           "acknowledged and the process continues in the background. Later on, the caller will be "
                           "notified whether the the operation succeeded or failed.\n\nTo ensure a vNSF can be "
                           "onboarded, the descriptors provided in the package need to be validated. These descriptors "
                           "are checked for:\n\n* Syntax errors to prevent incorrect vNSF descriptors.\n* vNSF "
                           "topology integrity to avoid potential loops or errors such as references to undefined "
                           "network interfaces.\n\nEvery onboarded vNSF descriptor will be checked for syntax, "
                           "correctness and completeness issues. With no issues found the next step is to check the "
                           "defined network topology and ensure inconsistencies such as no unconnected interfaces are "
                           "present and all links are properly defined. Upon successful validation, the vNSF may "
                           "proceed with the onboarding process. Any error results in a notification to the Developer "
                           "stating what is not compliant with the SHIELD requirements.",
            'consumes': ['multipart/form-data'],
            'responses': http_utils.responses_created
            },
        'get': {
            'summary': 'Lists all the vNSFs',
            'description': 'Provides a list of all the onboarded vNSFs along with a brief description for each one.',
            'responses': http_utils.responses_read
            }
        },
    '/vnsfs/{vnsfsId}': {
        'get': {
            'summary': 'Provides the details on a vNSF',
            'description': 'Provides all the information on the onboarded vNSF.',
            'responses': http_utils.responses_read
            },
        'delete': {
            'summary': 'Decommissions a vNSF',
            'description': "Takes a vNSF out of service which prevents it from ever being instantiated again.For a "
                           "running NS or vNSF a graceful decommission is provided through the schedule of the "
                           "operation for a later date.",
            'responses': http_utils.responses_deleted
            }
        }
    }
