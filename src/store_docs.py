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

from dashboardutils import http_codes

swagger_info = {
    'title': 'Dashboard API',
    'version': '0.1.0',
    'description': """
                   This API handles the security recommendations CRUD operations.


                   _Please note that consumers are not allowed to edit (`PATCH`), update (`PUT`) or delete (`DELETE`) 
                   a resource unless they provide an up-to-date `ETag` for the resource they are attempting to modify. 
                   This value, taken from the details (`GET`) request, is mandatory and should be provided in the 
                   `If-Match` header_.


                   API version numbering as per http://semver.org/
                   """,
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
    '/policies': {
        'get': {
            'summary': 'Lists all the security recommendations',
            'description': 'Provides a list of all the recommendations along with a description for each one.',
            'responses': http_codes.responses_read
        }
    },
    '/policies/{policiesId}': {
        'get': {
            'summary': 'Provides the details on a security recommendation',
            'description': 'Provides all the information on the security recommendation.',
            'responses': http_codes.responses_read
        },
        'patch': {
            'summary': 'Conveys the security recommendation to the Orchestrator',
            'description': "Forwards the security recommendation to the Orchestrator waiting for it’s reply.",
            'responses': http_codes.responses_updated
        }
    },
    '/admin/policies': {
        'post': {
            'summary': 'Persists a new security recommendation',
            'description': 'Stores a security recommendation and marks it as not applied.',
            'responses': http_codes.responses_created
        }
    }
}
