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

from abc import abstractmethod, ABCMeta
from storeutils import exceptions, http_utils

# Onboarding package-related.
PKG_MISSING_VNFD = 'vNSF Descriptor not found where manifest.yaml places it'
PKG_MISSING_NSD = 'Network Service Descriptor not found where manifest.yaml places it'
PKG_NOT_VNSFO = 'Package does not comply with the vNSFO format'
ONBOARDING_ISSUE = 'Can not onboard the package into the vNFSO'
VNSFO_UNREACHABLE = 'Can not reach the Orchestrator'
POLICY_ISSUE = 'Can not convey policy to the vNFSO'


class VnsfoVnsfWrongPackageFormat(exceptions.ExceptionMessage):
    """Wrong vNSFO package format."""


class VnsfoMissingVnfDescriptor(exceptions.ExceptionMessage):
    """Missing vNSF Descriptor from the package."""


class VnsfoNsWrongPackageFormat(exceptions.ExceptionMessage):
    """Wrong Network Descriptor package format."""


class VnsfoMissingNsDescriptor(exceptions.ExceptionMessage):
    """Missing Network Service Descriptor from the package."""


class VnsfOrchestratorOnboardingIssue(exceptions.ExceptionMessage):
    """vNSFO onboarding operation failed."""


class VnsfOrchestratorPolicyIssue(exceptions.ExceptionMessage):
    """vNSFO policy operation failed."""


class VnsfOrchestratorUnreacheable(exceptions.ExceptionMessage):
    """vNSFO cannot be reached."""


class VnsfOrchestratorAdapter(metaclass=ABCMeta):
    """
    Interface with the vNSF Orchestrator through it's Service Orquestrator REST API.

    The documentation available at the time of coding this is for OSM Release One (March 1, 2017) and can be found at
    https://osm.etsi.org/wikipub/images/2/24/Osm-r1-so-rest-api-guide.pdf. Despite the apparently straight forward
    way for onboarding vNSF & NS referred by the documentation the endpoints mentioned are not available outside
    localhost. Thus a workaround is required to get this to work.

    Such workaround consist in using the REST interface provided by the composer available at
    OSM/UI/skyquake/plugins/composer/routes.js and which implementation is at
    OSM/UI/skyquake/plugins/composer/api/composer.js. From these two files one can actually find the Service
    Orquestrator REST API endpoints being called to perform the required operation. From there it's just a matter of
    calling the proper composer endpoint so it can carry out the intended operation. Ain't life great?!
    """

    def __init__(self, protocol, server, port, api_basepath, logger=None):
        self.logger = logger or logging.getLogger(__name__)

        # Maintenance friendly.
        self._wrong_vnsf_package_format = VnsfoVnsfWrongPackageFormat(PKG_NOT_VNSFO)
        self._missing_vnsf_descriptor = VnsfoMissingVnfDescriptor(PKG_MISSING_VNFD)
        self._wrong_ns_package_format = VnsfoNsWrongPackageFormat(PKG_NOT_VNSFO)
        self._missing_ns_descriptor = VnsfoMissingNsDescriptor(PKG_MISSING_NSD)
        self._onboarding_issue = VnsfOrchestratorOnboardingIssue(ONBOARDING_ISSUE)
        self._unreachable = VnsfOrchestratorUnreacheable(VNSFO_UNREACHABLE)
        self._policy_issue = VnsfOrchestratorPolicyIssue(POLICY_ISSUE)

        self.basepath = http_utils.build_url(protocol, server, port, api_basepath)

        self.logger.debug('vNSF Orchestrator API at: %s', self.basepath)

    @abstractmethod
    def apply_policy(self, tenant_id, policy):
        """
        Sends a security policy to the Orchestrator.

        :param tenant_id: The tenant to apply the policy to.
        :param policy: The security policy data.
        """

        pass

    @abstractmethod
    def onboard_vnsf(self, tenant_id, vnsf_package_path, vnsfd_file):
        """
        Onboards a vNSF with the Orchestrator.

        :param tenant_id: The tenant where to onboard the vNSF.
        :param vnsf_package_path: The file system path where the vNSF package is stored.
        :param vnsfd_file: The relative path to the VNF Descriptor within the package.

        :return: the VNF package data.
        """

        pass

    @abstractmethod
    def onboard_ns(self, tenant_id, ns_package_path, nsd_file):
        """
        Onboards a vNSF with the Orchestrator.

        :param tenant_id: The tenant where to onboard the Network Service.
        :param ns_package_path: The file system path where the Network Service package is stored.
        :param nsd_file: The relative path to the Network Service Descriptor within the package.

        :return: the Network Service package data.
        """

        pass
