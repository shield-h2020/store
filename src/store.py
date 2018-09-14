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
import settings as cfg
import store_docs
from eve import Eve
from eve_swagger import swagger, add_documentation
from ns_hooks import NsHooks
from storeutils import log
from vnsf_hooks import VnsfHooks
from flask_cors import CORS
import flask
from flask import jsonify
from werkzeug.exceptions import default_exceptions


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
CORS(app)

# vNSF hooks.
app.on_pre_POST_vnsfs += VnsfHooks.onboard_vnsf
app.on_fetched_item_vnsfs += VnsfHooks.send_minimal_vnsf_data
app.on_post_GET_attestation += send_attestation

# Network Services hooks.
app.on_pre_POST_nss += NsHooks.onboard_ns

app.register_blueprint(swagger)

app.config['SWAGGER_INFO'] = store_docs.swagger_info

add_documentation({'paths': store_docs.paths})

if __name__ == '__main__':
    log.setup_logging(config_file='src/logging.yaml')
    logger = logging.getLogger(__name__)

    # use '0.0.0.0' to ensure your REST API is reachable from all your
    # network (and not only your computer).
    app.run(host='0.0.0.0', port=cfg.BACKENDAPI_PORT, debug=True)
