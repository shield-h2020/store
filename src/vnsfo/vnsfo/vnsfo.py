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


from storeutils import error_utils

from .osm_vnsfo import OsmVnsfoAdapter


class VnsfoNotSupported(error_utils.ExceptionMessage_):
    """Requested orchestrator isn't supported."""


class VnsfoFactory(object):
    """
    Orchestrator factory for vNSF.
    """

    @staticmethod
    def get_orchestrator(kind, protocol, server, port, api_basepath, logger=None):
        """
        Instantiates the vNSFO Orchestrator following the type provided.

        :param kind: the Orchestrator to instantiate.
        :param protocol: HTTP or HTTPS.
        :param server: the server name or IP address.
        :param port: the TCP port to reach the Orchestrator.
        :param api_basepath: the Ochestrator base path to its API.
        :return: the proper vNSF Orchestrator instance.
        """

        # Currently supported Orchestrator.
        supported = {
            'OSM-R2': OsmVnsfoAdapter,
            'OSM-R4': OsmVnsfoAdapter
            }

        orchestrator = supported.get(kind)(protocol, server, port, api_basepath, logger)
        if orchestrator is None:
            raise VnsfoNotSupported("Requested orchestrator isn't supported.")

        return orchestrator
