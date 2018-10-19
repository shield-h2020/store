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


import logging

import flask
import settings as cfg
from eve.methods.post import post_internal
from flask import abort, make_response, jsonify
from ns.ns import NsHelper, NsMissingPackage, NsWrongPackageFormat, NsPackageCompliance, NsWrongManifestFormat
from storeutils import http_utils
from storeutils.error_utils import IssueHandling, IssueElement
from vnsfo.vnsfo import VnsfoFactory
from vnsfo.vnsfo_adapter import VnsfoMissingNsDescriptor, VnsfOrchestratorOnboardingIssue, \
    VnsfoNsWrongPackageFormat, VnsfOrchestratorUnreacheable, NsValidationIssue, NsMissingDependency, \
    NsInvalidFormat, VnsfOrchestratorDeletingIssue
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import *

PKG_MISSING_FILE = 'No package provided'


class NsHooks:
    """
    Handles the backstage operations required for the Network Service Store API. These operations are mostly targeted
    at pre and post hooks associated with the API.
    """

    logger = logging.getLogger(__name__)
    issue = IssueHandling(logger)

    errors = {
        'ONBOARD_NS': {
            'PACKAGE_MISSING':       {
                IssueElement.ERROR.name:     [
                    "Missing or wrong field in POST. 'package' should be used as the field name"],
                IssueElement.EXCEPTION.name: NsMissingPackage('Can not onboard the package into the vNFSO')
                },
            'PACKAGE_ISSUE':         {
                IssueElement.ERROR.name:     ['{}'],
                IssueElement.EXCEPTION.name: PreconditionFailed()
                },
            'PACKAGE_COMPLIANCE':    {
                IssueElement.ERROR.name:     ['{}'],
                IssueElement.EXCEPTION.name: NotAcceptable()
                },
            'NS_VALIDATION_FAILURE': {
                IssueElement.ERROR.name:     ['{}'],
                IssueElement.EXCEPTION.name: UnprocessableEntity(),
                },
            'VNSFO_ISSUE':           {
                IssueElement.ERROR.name:     ['{}'],
                IssueElement.EXCEPTION.name: BadGateway()
                }
            },
        'DELETE_NS':  {
            'VNSFO_ISSUE': {
                IssueElement.ERROR.name:     ['{}'],
                IssueElement.EXCEPTION.name: BadGateway()
                }
            }
        }

    @staticmethod
    def onboard_ns(request):
        """
        Registers a Network Service into the Store and onboards it with the Orchestrator.

        The SHIELD manifest is checked for integrity and compliance. Metadata is stored for the catalogue and the actual
        manifest file is stored as binary so it can be provided for attestation purposes (thus ensuring
        tamper-proofing).

        :param request: the HTTP request data, holding a single Network Service package. If more than one package
        file is provided it gets ignored.
        """

        # Store validation data about the vnsf
        validation_data = dict()

        ex_response = None
        form_data = request.form.copy()

        try:
            # It's assumed that only one NS package file is received.
            if 'package' not in request.files:
                ex_response = NsHooks.issue.build_ex(
                        IssueElement.ERROR,
                        NsHooks.errors['ONBOARD_NS']['PACKAGE_MISSING'],
                        message="Missing or wrong field in POST. 'package' should be used as the field name"
                        )
                return

            vnsfo = VnsfoFactory.get_orchestrator('OSM', cfg.VNSFO_PROTOCOL, cfg.VNSFO_HOST, cfg.VNSFO_PORT,
                                                  cfg.VNSFO_API)

            ns = NsHelper(vnsfo)
            manifest_fs, package_data = ns.onboard_ns(cfg.VNSFO_TENANT_ID, request.files['package'], validation_data)

            # Ensure the SHIELD manifest is stored as a binary file.
            # NOTE: the file is closed by Eve once stored.
            files = request.files.copy()
            files['manifest_file'] = manifest_fs
            # The package field is only required for onboarding schema validation but shouldn't be stored as document
            # data.
            files.pop('package')
            request.files = ImmutableMultiDict(files)

            # Convert the Network Service package into the document data.
            # NOTE: there's no need to deep copy as the data won't be modified until it gets stored in the database.
            form_data['owner_id'] = '12ab34567c89d0123e4f5678'
            form_data['state'] = 'sandboxed'
            form_data['manifest'] = package_data['manifest']
            form_data['descriptor'] = package_data['descriptor']
            form_data['ns_id'] = package_data['ns_id']
            form_data['ns_name'] = package_data['ns_name']
            form_data['constituent_vnsfs'] = package_data['constituent_vnsfs']

        except (NsMissingPackage, NsWrongPackageFormat, VnsfoNsWrongPackageFormat) as e:
            ex_response = NsHooks.issue.build_ex(
                    IssueElement.ERROR, NsHooks.errors['ONBOARD_NS']['PACKAGE_ISSUE'], [[e.message]], e.message
                    )

        except (NsPackageCompliance, VnsfoMissingNsDescriptor, NsWrongManifestFormat) as e:
            ex_response = NsHooks.issue.build_ex(
                    IssueElement.ERROR, NsHooks.errors['ONBOARD_NS']['PACKAGE_COMPLIANCE'], [[e.message]], e.message
                    )

        except (VnsfOrchestratorOnboardingIssue, VnsfOrchestratorUnreacheable) as e:
            ex_response = NsHooks.issue.build_ex(
                    IssueElement.ERROR, NsHooks.errors['ONBOARD_NS']['VNSFO_ISSUE'], [[e.message]], e.message
                    )

        except (NsInvalidFormat, NsMissingDependency, NsValidationIssue) as e:
            ex_response = NsHooks.issue.build_ex(
                    IssueElement.ERROR, NsHooks.errors['ONBOARD_NS']['NS_VALIDATION_FAILURE'], [[e.message]], e.message
                    )

        finally:
            # Always persist the validation data, if existent
            validation_ref = None
            if validation_data:
                app = flask.current_app
                with app.test_request_context():
                    r, _, _, status, _ = post_internal('validation', validation_data)
                assert status == http_utils.HTTP_201_CREATED
                validation_ref = r['_id']

            # Check if exceptions were raised during the onboard process
            if ex_response:
                # Include validation data in the error response, if existent
                if validation_ref:
                    ex_response['validation'] = str(validation_ref)

                # Abort the request and reply with a meaningful error
                abort(make_response(jsonify(**ex_response), ex_response['_error']['code']))

            # Onboard succeeded. Include the validation reference in the request form
            if validation_ref:
                form_data['validation'] = validation_ref
            # Modify the request form to persist
            request.form = ImmutableMultiDict(form_data)

    @staticmethod
    def delete_ns(item):
        print("Solicited delete ", item['ns_id'])

        try:
            vnsfo = VnsfoFactory.get_orchestrator('OSM', cfg.VNSFO_PROTOCOL, cfg.VNSFO_HOST, cfg.VNSFO_PORT,
                                                  cfg.VNSFO_API)
            ns = NsHelper(vnsfo)
            ns.delete_ns(cfg.VNSFO_TENANT_ID, item['ns_id'])

        except (VnsfOrchestratorDeletingIssue, VnsfOrchestratorUnreacheable) as e:
            ex_response = NsHooks.issue.build_ex(
                    IssueElement.ERROR, NsHooks.errors['DELETE_NS']['VNSFO_ISSUE'], [[e.message]], e.message
                    )
            # Abort the request and reply with a meaningful error
            abort(make_response(jsonify(**ex_response), ex_response['_error']['code']))
