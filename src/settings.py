# -*- coding: utf-8 -*-

import os

API_PORT = int(os.environ.get('API_PORT', 5000))

MONGO_HOST = os.environ.get('DATASTORE_HOST', 'data-store')
MONGO_PORT = os.environ.get('DATASTORE_PORT', 27017)
MONGO_USERNAME = os.environ.get('DATASTORE_USERNAME', 'user')
MONGO_PASSWORD = os.environ.get('DATASTORE_PASSWORD', 'user')
MONGO_DBNAME = os.environ.get('DATASTORE_DBNAME', 'shield-store')

VNSFO_PROTOCOL = os.environ.get('VNSFO_PROTOCOL', 'http')
VNSFO_HOST = os.environ.get('VNSFO_HOST', '__missing_vnsfo_address__')
VNSFO_PORT = os.environ.get('VNSFO_PORT', '')
VNSFO_API = os.environ.get('VNSFO_API', '__missing_vnsfo_api_basepath__')

# NOTE: this shall be removed once AAA is in place.
VNSFO_TENANT_ID = os.environ.get('VNSFO_TENANT_ID', '__no_tenant_set__')

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

# Schema definition, based on Cerberus grammar. Check the Cerberus project
# (https://github.com/pyeve/cerberus) for details.

vnsf_model = {
    # vNSF "pedigree".
    'registry': {
        'type': 'dict',
        'required': True,
        'schema': {
            'vendor': {'type': 'string', 'empty': False, 'required': True},
            'capabilities': {'type': 'list', 'empty': False, 'required': True},
        }
    },
    'state': {
        'type': 'string',
        'empty': False,
        'allowed': ["submitted", "sandboxed", "onboarded", "decommissioned"],
        'required': True
    },

    # Manifest details.
    'manifest': {
        'type': 'dict',
        'required': True,
        'schema': {
            'manifest:vnsf': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'descriptor': {'type': 'string', 'empty': False, 'required': True},
                    'type': {'type': 'string', 'empty': False, 'allowed': ["OSM"], 'required': True},

                    #
                    # Due to a swagger editor bug the suitable name for this property can not be used.
                    # #1375 - cannot use a property named "security" (
                    # https://github.com/swagger-api/swagger-editor/issues/1375)
                    #
                    'security_info': {
                        'type': 'dict',
                        'required': True,
                        'schema': {
                            'vdu': {
                                'type': 'list',
                                'required': True,
                                'schema': {
                                    'type': 'dict',
                                    'schema': {
                                        'id': {'type': 'string', 'empty': False, 'required': True},
                                        'hash': {'type': 'string', 'empty': False, 'required': True},
                                        'attestation': {
                                            'type': 'dict',
                                            'required': True,
                                            'schema': {
                                                'somekey': {'type': 'string', 'empty': False, 'required': True}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },

    # Actual vNSF Descriptor.
    'descriptor': {'type': 'string', 'required': True},

    # Actual manifest binary.
    'manifest_file': {'type': 'media'},

    # Needed (for onboarding vNSFs) as the parameter name for the package file. After the POST it's no longer used.
    'package': {'type': 'media'}
}

vnsfs = {
    # 'title' tag used in item links.
    'item_title': 'vnsfs',
    'schema': vnsf_model,
    'resource_methods': ['POST', 'GET', 'DELETE'],
    # 'datasource': {
    #     'projection': {'package': 0}
    # }
}

vnsf_attestation = {
    'url': 'vnsfs/attestation',
    'schema': vnsf_model,
    'datasource': {
        'source': 'vnsfs'
    },
    'resource_methods': ['GET'],
    'hateoas': False,
}

# The DOMAIN dict explains which resources will be available and how they will
# be accessible to the API consumer.
DOMAIN = {
    'vnsfs': vnsfs,
    'attestation': vnsf_attestation
}
