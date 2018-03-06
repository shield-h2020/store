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

import settings as cfg
from ns.ns import NsHelper, NsMissingPackage, NsWrongPackageFormat, NsPackageCompliance
from vnsfo.vnsfo import VnsfoFactory
from vnsfo.vnsfo_adapter import VnsfoMissingNsDescriptor, VnsfOrchestratorOnboardingIssue, \
    VnsfoNsWrongPackageFormat, VnsfOrchestratorUnreacheable
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import *

PKG_MISSING_FILE = 'No package provided'


class NsHooks:
    """
    Handles the backstage operations required for the Network Service Store API. These operations are mostly targeted
    at pre and post hooks associated with the API.
    """

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

        logger = logging.getLogger(__name__)

        try:
            # It's assumed that only one NS package file is received.
            if 'package' not in request.files:
                logger.error("Missing or wrong field in POST. 'package' should be used as the field name")
                raise NsMissingPackage(PKG_MISSING_FILE)

            vnsfo = VnsfoFactory.get_orchestrator('OSM', cfg.VNSFO_PROTOCOL, cfg.VNSFO_HOST, cfg.VNSFO_PORT,
                                                  cfg.VNSFO_API)

            ns = NsHelper(vnsfo)
            manifest_fs, package_data = ns.onboard_ns(cfg.VNSFO_TENANT_ID, request.files['package'])

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
            form_data = request.form.copy()
            form_data['owner_id'] = '12ab34567c89d0123e4f5678'
            form_data['state'] = 'sandboxed'
            form_data['manifest'] = package_data['manifest']
            form_data['descriptor'] = package_data['descriptor']
            request.form = ImmutableMultiDict(form_data)

        except (NsMissingPackage, NsWrongPackageFormat, VnsfoNsWrongPackageFormat) as e:
            logger.error(e)
            raise PreconditionFailed(e.message)

        except (NsPackageCompliance, VnsfoMissingNsDescriptor) as e:
            logger.error(e)
            raise NotAcceptable(e.message)

        except (VnsfOrchestratorOnboardingIssue, VnsfOrchestratorUnreacheable) as e:
            logger.error(e)
            raise BadGateway(e.message)
