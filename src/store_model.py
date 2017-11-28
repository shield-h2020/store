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


policy_model = {
    # The tenant to whom the policy is for.
    'tenant_id': {
        'description': 'Description of the user resource',
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

vnsf_model = {
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
                    'type': {'type': 'string', 'empty': False, 'allowed': ["OSM"], 'required': True},
                    'package': {'type': 'string', 'empty': False, 'required': True},
                    'descriptor': {'type': 'string', 'empty': False, 'required': True},

                    # vNSF "pedigree".
                    'registry': {
                        'type': 'dict',
                        'required': True,
                        'schema': {
                            'vendor': {'type': 'string', 'empty': False, 'required': True},
                            'capabilities': {'type': 'list', 'empty': False, 'required': True},
                            }
                        },

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

ns_model = {
    # To whom this Network Service belongs to.
    'owner_id': {
        'type': 'objectid',
        'empty': False,
        'required': True
        },

    # The current state of the Network Service.
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
            'manifest:ns': {
                'type': 'dict',
                'required': True,
                'schema': {
                    # The package schema used.
                    'type': {
                        'type': 'string',
                        'empty': False,
                        'allowed': ["OSM"],
                        'required': True},

                    # Name of the package file.
                    'package': {
                        'type': 'string', 'empty': False, 'required': True},

                    # (Relative) Path to the descriptor file, including the file name and extension, once the files
                    # are decompressed.
                    'descriptor': {'type': 'string', 'empty': False, 'required': True},

                    # NS "pedigree".
                    'registry': {
                        'type': 'dict',
                        'required': True,
                        'schema': {
                            'capabilities': {'type': 'list', 'empty': False, 'required': True},
                            }
                        },
                    }
                }
            }
        },

    # Actual NS Descriptor.
    'descriptor': {'type': 'string', 'required': True},

    # Actual manifest binary.
    'manifest_file': {'type': 'media'},

    # Needed (for onboarding NSs) as the parameter name for the package file. After the POST it's no longer used.
    'package': {'type': 'media'}
    }
