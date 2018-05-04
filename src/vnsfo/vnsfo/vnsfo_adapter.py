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
from storeutils import http_utils
from storeutils.error_utils import ExceptionMessage_, IssueHandling, IssueElement


class VnsfoVnsfWrongPackageFormat(ExceptionMessage_):
    """Wrong vNSFO package format."""


class VnsfoMissingVnfDescriptor(ExceptionMessage_):
    """Missing vNSF Descriptor from the package."""


class VnsfoNsWrongPackageFormat(ExceptionMessage_):
    """Wrong Network Descriptor package format."""


class VnsfoMissingNsDescriptor(ExceptionMessage_):
    """Missing Network Service Descriptor from the package."""


class VnsfOrchestratorOnboardingIssue(ExceptionMessage_):
    """vNSFO onboarding operation failed."""


class VnsfOrchestratorPolicyIssue(ExceptionMessage_):
    """vNSFO policy operation failed."""


class VnsfOrchestratorUnreacheable(ExceptionMessage_):
    """vNSFO cannot be reached."""


class VnsfInvalidFormat(ExceptionMessage_):
    """vNSF descriptor has an invalid format"""

class VnsfValidationIssue(ExceptionMessage_):
    """Issues occurred when validating vNSF descriptor"""

class NsInvalidFormat(ExceptionMessage_):
    """NS descriptor has an invalid format"""

class NsValidationIssue(ExceptionMessage_):
    """Issues occurred when validating NS descriptor"""


class VnsfOrchestratorAdapter(object, metaclass=ABCMeta):
    """
    Define the interface for a vNSF Orchestrator. Each implementation must tailor its behaviour to the Orchestrator it
    interacts with.
    """

    errors = {
        'ONBOARD_VNSF': {
            'PKG_MISSING_VNFD_FOLDER': {
                IssueElement.ERROR.name: ["Missing VNF folder. Expected at '{}'"],
                IssueElement.EXCEPTION.name: VnsfoMissingVnfDescriptor(
                        'vNSF Descriptor not found where manifest.yaml places it')
                },
            'PKG_MISSING_VNFD': {
                IssueElement.ERROR.name: ["Missing VNFD. Expected at '{}'"],
                IssueElement.EXCEPTION.name: VnsfoMissingVnfDescriptor(
                        'vNSF Descriptor not found where manifest.yaml places it')
                },
            'ONBOARDING_ISSUE': {
                IssueElement.ERROR.name: ['vNFSO onboarding at {}. Msg: {} | Status: {}'],
                IssueElement.EXCEPTION.name: VnsfOrchestratorOnboardingIssue(
                        'Can not onboard the package into the vNFSO')
                },
            'VNSFPKG_NOT_VNSFO': {
                IssueElement.ERROR.name: ['Package does not comply with the vNSFO format'],
                IssueElement.EXCEPTION.name: VnsfOrchestratorUnreacheable(
                        'Package does not comply with the vNSFO format')
                },
            'VNSFO_UNREACHABLE': {
                IssueElement.ERROR.name: ['Error onboarding the vNSF at {}'],
                IssueElement.EXCEPTION.name: VnsfOrchestratorUnreacheable('Can not reach the Orchestrator')
                },
            'VNFD_FORMAT_INVALID': {
                IssueElement.ERROR.name: ['Invalid format of VNFD {}'],
                IssueElement.EXCEPTION.name: VnsfInvalidFormat('Can not read vNSF descriptor')
            },
            'VALIDATION_ERROR': {
                IssueElement.ERROR.name: ['Error validating vNSF descriptor: {}'],
                IssueElement.EXCEPTION.name: VnsfValidationIssue("Error validating vNSF descriptor")
                },

            },
        'ONBOARD_NS': {
            'PKG_MISSING_NS_FOLDER': {
                IssueElement.ERROR.name: ["Missing Network Service folder. Expected at '{}'"],
                IssueElement.EXCEPTION.name: VnsfoMissingVnfDescriptor(
                        'Network Service Descriptor not found where manifest.yaml places it')
                },
            'PKG_MISSING_NSD': {
                IssueElement.ERROR.name: ["Missing NSD. Expected at '{}'"],
                IssueElement.EXCEPTION.name: VnsfoMissingNsDescriptor(
                        'Network Service Descriptor not found where manifest.yaml places it')
                },
            'ONBOARDING_ISSUE': {
                IssueElement.ERROR.name: ['vNFSO onboarding at {}. Msg: {} | Status: {}'],
                IssueElement.EXCEPTION.name: VnsfOrchestratorOnboardingIssue(
                        'Can not onboard the package into the vNFSO')
                },
            'NSPKG_NOT_VNSFO': {
                IssueElement.ERROR.name: ['No package file provided in POST'],
                IssueElement.EXCEPTION.name: VnsfOrchestratorUnreacheable(
                        'Package does not comply with the vNSFO format')
                },
            'VNSFO_UNREACHABLE': {
                IssueElement.ERROR.name: ['Error onboarding the Network Service at {}'],
                IssueElement.EXCEPTION.name: VnsfOrchestratorUnreacheable('Can not reach the Orchestrator')
                },
            'NSD_FORMAT_INVALID': {
                IssueElement.ERROR.name: ['Invalid format of NSD {}'],
                IssueElement.EXCEPTION.name: NsInvalidFormat('Can not read NS descriptor')
            },
            'VALIDATION_ERROR': {
                IssueElement.ERROR.name: ['Error validating NS descriptor: {}'],
                IssueElement.EXCEPTION.name: NsValidationIssue("Error validating NS descriptor")
                },

            },
        'POLICY': {
            'POLICY_ISSUE': {
                IssueElement.ERROR.name: ['vNFSO policy at {}. Status: {}'],
                IssueElement.EXCEPTION.name: VnsfOrchestratorPolicyIssue('Can not convey policy to the vNFSO')
                },
            'VNSFO_UNREACHABLE': {
                IssueElement.ERROR.name: ['Error conveying policy at {}'],
                IssueElement.EXCEPTION.name: VnsfOrchestratorUnreacheable('Can not reach the Orchestrator')
                }
            }
        }

    def __init__(self, protocol, server, port, api_basepath, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.issue = IssueHandling(self.logger)

        self.basepath = http_utils.build_url(server, port, api_basepath, protocol)

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
    def onboard_vnsf(self, tenant_id, vnsf_package_path, vnsfd_file, validation_data):
        """
        Onboards a vNSF with the Orchestrator.

        :param tenant_id: The tenant where to onboard the vNSF.
        :param vnsf_package_path: The file system path where the vNSF package is stored.
        :param vnsfd_file: The relative path to the VNF Descriptor within the package.

        :return: the VNF package data.
        """

        pass

    @abstractmethod
    def onboard_ns(self, tenant_id, ns_package_path, nsd_file, validation_data):
        """
        Onboards a vNSF with the Orchestrator.

        :param tenant_id: The tenant where to onboard the Network Service.
        :param ns_package_path: The file system path where the Network Service package is stored.
        :param nsd_file: The relative path to the Network Service Descriptor within the package.

        :return: the Network Service package data.
        """

        pass
