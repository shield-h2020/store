# -*- coding: utf-8 -*-

"""
    eve-demo settings
    ~~~~~~~~~~~~~~~~~

    Settings file for our little demo.

    PLEASE NOTE: We don't need to create the two collections in MongoDB.
    Actually, we don't even need to create the database: GET requests on an
    empty/non-existant DB will be served correctly ('200' OK with an empty
    collection); DELETE/PATCH will receive appropriate responses ('404' Not
    Found), and POST requests will create database and collections when needed.
    Keep in mind however that such an auto-managed database will most likely
    perform poorly since it lacks any sort of optimized index.

    :copyright: (c) 2016 by Nicola Iarocci.
    :license: BSD, see LICENSE for more details.
"""

import os

# We want to seamlessy run our API both locally and on Heroku. If running on
# Heroku, sensible DB connection settings are stored in environment variables.
MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = os.environ.get('MONGO_PORT', 27017)
MONGO_USERNAME = os.environ.get('MONGO_USERNAME', 'user')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', 'user')
MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'evedemo')

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

#######################
#######################
#
# Eve schema generation
# https://github.com/drud/evegenie
#
#######################
#######################


vnsfs = {
    # 'title' tag used in item links.
    'item_title': 'vnsfs',

    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/pyeve/cerberus) for details.
    'schema': {
        'state': {
            'type': 'string',
            'empty': False,
            'allowed': ["submitted", "sandboxed", "onboarded", "decommissioned"],
            'required': True
        },
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
        'descriptor': {'type': 'string', 'required': True},
        'manifest_file': {'type': 'media'},
        # Needed (for onboarding vNSFs) as the parameter name for the package file. After the POST it's no longer used.
        'package': {'type': 'media'},
        # 'datasource': {
        #     'projection': {'package': 0}
        # }
    },
    'resource_methods': ['POST', 'GET', 'DELETE'],
}

vnsf_attestation = {
    'url': 'vnsfs/attestation',
    'schema': vnsfs['schema'],
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
