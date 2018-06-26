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


import os

import store_endpoints

BACKENDAPI_PORT = int(os.environ.get('BACKENDAPI_PORT', 5000))

MONGO_HOST = os.environ.get('DATASTORE_HOST', 'data-store')
MONGO_PORT = int(os.environ.get('DATASTORE_PORT', 27017))
MONGO_USERNAME = os.environ.get('DATASTORE_USERNAME', 'user')
MONGO_PASSWORD = os.environ.get('DATASTORE_PASSWORD', 'user')
MONGO_DBNAME = os.environ.get('DATASTORE_DBNAME', 'shield-store')

VNSFO_PROTOCOL = os.environ.get('VNSFO_PROTOCOL', 'http')
VNSFO_HOST = os.environ.get('VNSFO_HOST', '__missing_vnsfo_address__')
VNSFO_PORT = os.environ.get('VNSFO_PORT', '')
VNSFO_API = os.environ.get('VNSFO_API', '__missing_vnsfo_api_basepath__')

# NOTE: this shall be removed once AAA is in place.
VNSFO_TENANT_ID = os.environ.get('VNSFO_TENANT_ID', '__no_tenant_set__')

X_DOMAINS = '*'  # CORS-related settings.
X_HEADERS = ['Content-Type', 'If-Match']

# Date format for fields to store - ISO 8601.
DATETIME_FIELDS_INPUT_FMT = '%Y-%m-%dT%H:%M:%S'

XML = False

# We enable standard client cache directives for all resources exposed by the
# API. We can always override these global settings later.
CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20

# Schema definition, based on Cerberus grammar. Check the Cerberus project
# (https://github.com/pyeve/cerberus) for details.

# The DOMAIN dict explains which resources will be available and how they will
# be accessible to the API consumer.
DOMAIN = {
    'vnsfs': store_endpoints.vnsfs,
    'nss': store_endpoints.nss,
    'attestation': store_endpoints.vnsf_attestation,
    'validation': store_endpoints.validation,
    }
