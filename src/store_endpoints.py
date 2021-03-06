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


import store_model

vnsfs = {
    'item_title': 'vnsfs',
    'schema': store_model.vnsf_model,
    'resource_methods': ['POST', 'GET'],
    'item_methods': ['GET', 'DELETE'],
    'additional_lookup': {
         'url': 'regex("[\w]+")',
         'field': 'vnsf_id'
    }
}

vnsf_attestation = {
    'url': 'attestation/vnsfs',
    'schema': store_model.vnsf_model,
    'datasource': {
        'source': 'vnsfs',
        },
    'resource_methods': ['GET'],
    'hateoas': False,
    'additional_lookup': {
         'url': 'regex("[\w]+")',
         'field': 'vnsf_id'
    }
}

nss = {
    'item_title': 'nss',
    'schema': store_model.ns_model,
    'resource_methods': ['POST', 'GET'],
    'item_methods': ['GET', 'DELETE'],
    'additional_lookup': {
         'url': 'regex("[\w]+")',
         'field': 'ns_id'
    }
}

validation = {
    'item_title': 'validation',
    'schema': store_model.validation_model,
    'resource_methods': ['POST', 'GET'],
    'item_methods': ['GET', 'DELETE'],
}
