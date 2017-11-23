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

BACKENDAPI_PORT = int(os.environ.get('BACKENDAPI_PORT', 4000))

MONGO_HOST = os.environ.get('DATASTORE_HOST', 'dashboard-persistence')
MONGO_PORT = os.environ.get('DATASTORE_PORT', 27017)
MONGO_USERNAME = os.environ.get('DATASTORE_USERNAME', 'user')
MONGO_PASSWORD = os.environ.get('DATASTORE_PASSWORD', 'user')
MONGO_DBNAME = os.environ.get('DATASTORE_DBNAME', 'shield-dashboard')

VNSFO_PROTOCOL = os.environ.get('VNSFO_PROTOCOL', 'http')
VNSFO_HOST = os.environ.get('VNSFO_HOST', '__missing_vnsfo_address__')
VNSFO_PORT = os.environ.get('VNSFO_PORT', '')
VNSFO_API = os.environ.get('VNSFO_API', '__missing_vnsfo_api_basepath__')

# NOTE: this shall be removed once AAA is in place.
VNSFO_TENANT_ID = os.environ.get('VNSFO_TENANT_ID', '__no_tenant_set__')

# CORS-related settings.
X_DOMAINS = '*'
X_HEADERS = ['Content-Type, ''If-Match']

#
# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Enable reads (GET), edits (PATCH) and deletes of individual items
# (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']

# We enable standard client cache directives for all resources exposed by the
# API. We can always override these global settings later.
CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20

# Date format for fields to store - ISO 8601.
DATETIME_FIELDS_INPUT_FMT = '%Y-%m-%dT%H:%M:%S'

# Schema definition, based on Cerberus grammar. Check the Cerberus project
# (https://github.com/pyeve/cerberus) for details.

policy_model = {
    # The tenant to whom the policy is for.
    'tenant_id': {
        'type': 'string',
        'empty': False,
        'required': True
    },

    # Time and date when the thread was detected. Format: ISO 8601.
    'detection': {
        # This field should be of type datetime. The problem here is that datetime isn't JSON serializable so a
        # string must be sent. The trick is to convert the string to a datetime instance in a hook function.
        # The string type caters for the serialization to JSON so the type must match or Cerberus won't validate it
        # and so it never gets to the hook function. Once it gets to the hook function it is converted to datetime
        # and stored. Storing as datetime doesn't seem to be a problem as pymongo doesn't check the instance type (
        # the assumption is that it was previously validated by Cerberus so it won't check it again).
        # This is not the most elegant hack but it seems the most adequate given the constraints.
        'type': 'string',
        'empty': False,
        'required': True
    },

    # The severity assigned to the threat. Format: user-defined.
    'severity': {
        'type': 'integer',
        'empty': False,
        'required': True
    },

    # The applicability of the policy for the tenant in question. Format: user-defined.
    'status': {
        'type': 'string',
        'empty': False,
        'required': True
    },

    # The kind of network attack. Format: user-defined.
    'attack': {
        'type': 'string',
        'empty': False,
        'required': True
    },

    # The recommendation to counter the threat. Format: user-defined.
    'recommendation': {
        'type': 'string',
        'empty': False,
        'required': True
    }
}

policies = {
    # 'title' tag used in item links.
    'item_title': 'policies',
    'schema': policy_model,
    'resource_methods': ['GET']
}

policies_admin = {
    'url': 'admin/policies',
    'schema': policy_model,
    'datasource': {
        'source': 'policies'
    },
    'resource_methods': ['GET', 'POST', 'DELETE']
}

xpto = {
    'item_title': 'xpto',
    'schema': policy_model,
    'datasource': {
        'source': 'policies'
    },
    'resource_methods': ['GET', 'POST', 'DELETE']
}

# The DOMAIN dict explains which resources will be available and how they will
# be accessible to the API consumer.
DOMAIN = {
    'policies': policies,
    'policies_admin': policies_admin
}
