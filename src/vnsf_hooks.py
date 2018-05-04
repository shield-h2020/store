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
from eve.methods.post import post_internal
from storeutils import http_utils
from flask import abort, make_response, jsonify
import settings as cfg
from storeutils.error_utils import IssueHandling, IssueElement
from vnsf.vnsf import VnsfHelper, VnsfMissingPackage, VnsfWrongPackageFormat, VnsfPackageCompliance
from vnsfo.vnsfo import VnsfoFactory
from vnsfo.vnsfo_adapter import VnsfoMissingVnfDescriptor, VnsfOrchestratorOnboardingIssue, VnsfValidationIssue, \
    VnsfoVnsfWrongPackageFormat, VnsfOrchestratorUnreacheable
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import *

PKG_MISSING_FILE = 'No package provided'


class VnsfHooks:
    """
    Handles the backstage operations required for the vNSF Store API. These operations are mostly targeted
    at pre and post hooks associated with the API.
    """

    logger = logging.getLogger(__name__)

    issue = IssueHandling(logger)

    errors = {
        'ONBOARD_VNSF': {
            'PACKAGE_MISSING': {
                IssueElement.ERROR.name: ["Missing or wrong field in POST. 'package' should be used as the field name"],
                IssueElement.EXCEPTION.name: VnsfMissingPackage('Can not onboard the package into the vNFSO')
                },
            'PACKAGE_ISSUE': {
                IssueElement.ERROR.name: ['{}'],
                IssueElement.EXCEPTION.name: PreconditionFailed()
                },
            'PACKAGE_COMPLIANCE': {
                IssueElement.ERROR.name: ['{}'],
                IssueElement.EXCEPTION.name: NotAcceptable()
                },
            'VNSF_VALIDATION_FAILURE': {
                IssueElement.ERROR.name: ['{}'],
                IssueElement.EXCEPTION.name: UnprocessableEntity(),
                },
            'VNSFO_ISSUE': {
                IssueElement.ERROR.name: ['{}'],
                IssueElement.EXCEPTION.name: PreconditionRequired()
                }
            }
        }

    @staticmethod
    def onboard_vnsf(request):
        """
        Registers a vNSF into the Store and onboards it with the Orchestrator.

        The SHIELD manifest is checked for integrity and compliance. Metadata is stored for the catalogue and the actual
        manifest file is stored as binary so it can be provided for attestation purposes (thus ensuring
        tamper-proofing).

        :param request: the HTTP request data, holding a single vNSF package. If more than one package file is provided
        it gets ignored.
        """

        # Store validation data about the vnsf
        validation_data = dict()

        ex_response = None
        form_data = request.form.copy()

        try:
            # It's assumed that only one vNSF package file is received.
            if 'package' not in request.files:
                ex_response = VnsfHooks.issue.build_ex(
                    IssueElement.ERROR,
                    VnsfHooks.errors['ONBOARD_VNSF']['PACKAGE_MISSING'],
                    message="Missing or wrong field in POST. 'package' should be used as the field name"
                )
                return

            vnsfo = VnsfoFactory.get_orchestrator('OSM', cfg.VNSFO_PROTOCOL, cfg.VNSFO_HOST, cfg.VNSFO_PORT,
                                                  cfg.VNSFO_API)

            vnsf = VnsfHelper(vnsfo)

            manifest_fs, package_data = vnsf.onboard_vnsf(cfg.VNSFO_TENANT_ID, request.files['package'],
                                                          validation_data)

            # Ensure the SHIELD manifest is stored as a binary file.
            # NOTE: the file is closed by Eve once stored.
            files = request.files.copy()
            files['manifest_file'] = manifest_fs
            # The package field is only required for onboarding schema validation but shouldn't be stored as document
            # data.
            files.pop('package')
            request.files = ImmutableMultiDict(files)

            # Convert the vNSF package into the document data.
            # NOTE: there's no need to deep copy as the data won't be modified until it gets stored in the database.
            form_data['state'] = 'sandboxed'
            form_data['manifest'] = package_data['manifest']
            form_data['descriptor'] = package_data['descriptor']

        except (VnsfMissingPackage, VnsfWrongPackageFormat, VnsfoVnsfWrongPackageFormat) as e:
            ex_response = VnsfHooks.issue.build_ex(
                IssueElement.ERROR, VnsfHooks.errors['ONBOARD_VNSF']['PACKAGE_ISSUE'], [[e.message]], e.message
            )

        except (VnsfPackageCompliance, VnsfoMissingVnfDescriptor) as e:
            ex_response = VnsfHooks.issue.build_ex(
                IssueElement.ERROR, VnsfHooks.errors['ONBOARD_VNSF']['PACKAGE_COMPLIANCE'], [[e.message]], e.message
            )

        except (VnsfOrchestratorOnboardingIssue, VnsfOrchestratorUnreacheable) as e:
            ex_response = VnsfHooks.issue.build_ex(
                IssueElement.ERROR, VnsfHooks.errors['ONBOARD_VNSF']['VNSFO_ISSUE'], [[e.message]], e.message
            )

        except VnsfValidationIssue as e:
            ex_response = VnsfHooks.issue.build_ex(
                IssueElement.ERROR, VnsfHooks.errors['ONBOARD_VNSF']['VNSF_VALIDATION_FAILURE'], [[e.message]], e.message
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

    def send_minimal_vnsf_data(response):
        """
        Send the vNSF attestation-related data.

        :param response: the response from the DB
        :return: The vNSF with the "public" properties only.
        """

        del response['manifest_file']
        del response['state']
