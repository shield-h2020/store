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


import json
import logging

import base64
from eve import Eve
from flask import abort

import log
import settings as cfg
import store_errors as err
from vnsf import Vnsf, VnsfMissingPackage, VnsfWrongPackageFormat, VnsfPackageCompliance
from vnsfo import VnsfoMissingVnfDescriptor, VnsfOrchestratorOnboardingIssue, VnsfoVnsfWrongPackageFormat


def onboard_vnsf(request):
    """
    Registers a vNSF into the Store and onboards it with the Orchestrator.

    The SHIELD manifest is checked for integrity and compliance. Metadata is stored for the catalogue and the actual
    manifest file is stored as binary so it can be provided for attestation purposes (thus ensuring tamper-proofing).

    :param request: the HTTP request data.
    """

    try:
        vnsf = Vnsf()
        vnsf.onboard_vnsf(request)

    except (VnsfMissingPackage, VnsfWrongPackageFormat, VnsfoVnsfWrongPackageFormat) as e:
        abort(err.HTTP_412_PRECONDITION_FAILED, e.message)

    except (VnsfPackageCompliance, VnsfoMissingVnfDescriptor) as e:
        abort(err.HTTP_406_NOT_ACCEPTABLE, e.message)

    except VnsfOrchestratorOnboardingIssue as e:
        abort(err.HTTP_502_BAD_GATEWAY, e.message)


def send_minimal_vnsf_data(response):
    """
    Send the vNSF attestation-related data.

    :param response: the response from the DB
    :return: The vNSF with the "public" properties only.
    """

    del response['manifest_file']
    del response['state']


def send_attestation(request, response):
    """
    Send the vNSF attestation-related data.

    :param request: the actual request
    :param response: the response from the DB
    :return: The attestation data.
    """

    logger.info('Send attestation data only')

    payload_json = json.loads(response.get_data(as_text=True))
    response.set_data(base64.b64decode(payload_json['manifest_file']))

    response.headers['Content-Disposition'] = 'attachment;filename=a.zip'
    response.headers['Content-Type'] = 'application/octet-stream'


app = Eve()
app.on_pre_POST_vnsfs += onboard_vnsf
app.on_fetched_item_vnsfs += send_minimal_vnsf_data
app.on_post_GET_attestation += send_attestation

if __name__ == '__main__':
    log.setup_logging()
    logger = logging.getLogger(__name__)

    # use '0.0.0.0' to ensure your REST API is reachable from all your
    # network (and not only your computer).
    app.run(host='0.0.0.0', port=cfg.API_PORT, debug=True)
