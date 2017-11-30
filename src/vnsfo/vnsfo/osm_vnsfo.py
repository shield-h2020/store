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

import os
import requests
from shutil import rmtree
from storeutils import http_utils, tar_package
from tempfile import mkdtemp

from .vnsfo_adapter import VnsfOrchestratorAdapter, PKG_NOT_VNSFO


class OsmVnsfoAdapter(VnsfOrchestratorAdapter):
    """
    Open Source Mano Orchestrator adapter.
    """

    def __init__(self, protocol, server, port, api_basepath, logger=None):
        super().__init__(protocol, server, port, api_basepath, logger)
        self.logger = logger or logging.getLogger(__name__)

    def apply_policy(self, tenant_id, policy):
        """
        Sends a security policy through the Orchestrator REST interface.

        :param tenant_id: The tenant to apply the policy to.
        :param policy: The security policy data.
        """

        sec_policy = dict()
        sec_policy['action'] = 'set-policies'
        sec_policy['params'] = dict()
        sec_policy['params']['policy'] = policy['recommendation']

        self.logger.debug('Policy for Orchestrator: %r', json.dumps(sec_policy))

        url = '{}/{}'.format(self.basepath, 'vnsf/action')

        headers = {'Content-Type': 'application/json'}

        self.logger.debug("Send policy data to '%s'", url)

        try:
            r = requests.post(url, headers=headers, json=sec_policy, verify=False)

            if len(r.text) > 0:
                self.logger.debug(r.text)

            if not r.status_code == http_utils.HTTP_200_OK:
                self.logger.error('vNFSO policy at {}. Status: {}'.format(url, r.status_code))
                raise self._policy_issue

        except requests.exceptions.ConnectionError:
            self.logger.error('Error conveying policy at %s', url)
            raise self._unreachable

    def onboard_vnsf(self, tenant_id, vnsf_package_path, vnsfd_file):
        """
        Onboards a vNSF with the Orchestrator.

        For some reason OSM Release Two doesn't onboard VNF packages with files not referenced in the descriptor
        therefore this adapter must only onboard the VNF package with the files used by the OSM.
        NOTE: this conclusion was reached after try-outs onboarding a SHIELD vNSF compliant with the OSM VNF package
        specification. The onboarding was done using  he OSM Composer UI and the VNF used was the cirros_vnf.tar.gz (
        available at https://osm-download.etsi.org/ftp/examples/cirros_2vnf_ns/). The SHIELD vNSF wouldn't onboard
        but the OSM-compliant-VNF within the SHIELD package onboards without any issues whatsoever.

        :param tenant_id: The tenant where to onboard the vNSF.
        :param vnsf_package_path: The file system path where the OSM VNF package is stored.
        :param vnsfd_file: The relative path to the VNF Descriptor within the OSM VNF package.
        """

        # Extract the vNSF package details relevant for onboarding.
        package_data = self._parse_vnsf_package(vnsf_package_path, vnsfd_file)

        self.logger.debug("package data: %s", package_data)

        url = '{}/package/onboard'.format(self.basepath)

        # 'Content-Type': 'multipart/form-data' is set by the requests library.
        files = {'package': (os.path.split(vnsf_package_path)[1], open(vnsf_package_path, 'rb'))}

        self.logger.debug("Onboard vNSF package '%s' to '%s'", vnsf_package_path, url)

        try:
            r = requests.post(url, files=files, verify=False)

            if len(r.text) > 0:
                self.logger.debug(r.text)

            if not r.status_code == http_utils.HTTP_200_OK:
                self.logger.error('vNFSO onboarding at {}. Msg: {} | Status: {}'.format(url, r.reason, r.status_code))
                raise self._onboarding_issue

        except requests.exceptions.ConnectionError:
            self.logger.error('Error onboarding the vNSF at %s', url)
            raise self._unreachable

        return package_data

    def _parse_vnsf_package(self, vnf_package_path, vnfd_file):
        """
        Decompresses a vNF package and looks for the expected files and content according to what the vNSF
        Orchestrator is expecting.

        :param vnf_package_path: The file system path to the vNSF package (.tar.gz) file.
        :param vnfd_file: The path to where the vNSF Descriptor file (<name>_vnfd.yaml) is located within the package.

        :return: The vNSF package data relevant to the onboarding operation.
        """

        # The vNSF package must be in '.tar.gz' format.
        if not tar_package.is_tar_gz_file(vnf_package_path):
            self.logger.error(PKG_NOT_VNSFO)
            raise self._wrong_vnsf_package_format

        extracted_package_path = mkdtemp()

        tar_package.extract_package(vnf_package_path, extracted_package_path)

        self.logger.debug('extracted package path: %s', extracted_package_path)
        self.logger.debug('extracted contents: %s', os.listdir(extracted_package_path))

        # The vNF package folder must exist. The folder name is the same as the VNF package one with .tar.gz removed.
        vnf_folder_abs_path = os.path.join(extracted_package_path, tar_package.get_tar_gz_basename(vnf_package_path))
        if not os.path.isdir(vnf_folder_abs_path):
            self.logger.error("Missing VNF folder. Expected at '%s'", vnf_folder_abs_path)
            raise self._missing_vnsf_descriptor

        self.logger.debug('vNSFO package: %s', os.listdir(vnf_folder_abs_path))
        self.logger.debug('VNFD path: %s', vnfd_file)

        # The vNSF Descriptor must be in the expected location so it's contents can be retrieved.
        vnfd_file_abs_path = os.path.join(extracted_package_path, vnfd_file)
        if not os.path.isfile(vnfd_file_abs_path):
            self.logger.error("Missing VNFD. Expected at '%s'", vnfd_file)
            raise self._missing_vnsf_descriptor
        with open(vnfd_file_abs_path, 'r') as stream:
            vnsfd = stream.read()

        self.logger.debug('VNFD\n%s', vnsfd)

        # Set the vNSF package data useful for the onboarding operation.
        package_data = {'descriptor': vnsfd}

        rmtree(extracted_package_path)

        return package_data

    def onboard_ns(self, tenant_id, ns_package_path, nsd_file):
        """
        Onboards a vNSF with the Orchestrator.

        :param tenant_id: The tenant where to onboard the Network Service.
        :param ns_package_path: The file system path where the Network Service package is stored.
        :param nsd_file: The relative path to the Network Service Descriptor within the package.

        :return: the Network Service package data.
        """

        # Extract the Network Service package details relevant for onboarding.
        package_data = self._parse_ns_package(ns_package_path, nsd_file)

        self.logger.debug("package data: %s", package_data)

        url = '{}/package/onboard'.format(self.basepath)

        files = {'package': (os.path.split(ns_package_path)[1], open(ns_package_path, 'rb'))}

        self.logger.debug("Onboard Network Service package '%s' to '%s'", ns_package_path, url)

        try:
            r = requests.post(url, files=files, verify=False)

            if len(r.text) > 0:
                self.logger.debug(r.text)

            if not r.status_code == http_utils.HTTP_200_OK:
                self.logger.error('vNFSO onboarding at {}. Msg: {} | Status: {}'.format(url, r.reason, r.status_code))
                raise self._onboarding_issue

        except requests.exceptions.ConnectionError:
            self.logger.error('Error onboarding the Network Service at %s', url)
            raise self._unreachable

        return package_data

    def _parse_ns_package(self, ns_package_path, nsd_file):
        """
        Decompresses a Network Service package and looks for the expected files and content according to what the vNSF
        Orchestrator is expecting.

        :param ns_package_path: The file system path to the Network Service package (.tar.gz) file.
        :param nsd_file: The path to where the Network Service Descriptor file (<name>_nsd.yaml) is located within
        the package.

        :return: The Network Service package data relevant to the onboarding operation.
        """

        # The Network Service package must be in '.tar.gz' format.
        if not tar_package.is_tar_gz_file(ns_package_path):
            self.logger.error(PKG_NOT_VNSFO)
            raise self._wrong_ns_package_format

        extracted_package_path = mkdtemp()

        tar_package.extract_package(ns_package_path, extracted_package_path)

        self.logger.debug('extracted package path: %s', extracted_package_path)
        self.logger.debug('extracted contents: %s', os.listdir(extracted_package_path))

        # The Network Service package folder must exist. The folder name is the same as the Network Service package
        # one with .tar.gz removed.
        ns_folder_abs_path = os.path.join(extracted_package_path, tar_package.get_tar_gz_basename(ns_package_path))
        if not os.path.isdir(ns_folder_abs_path):
            self.logger.error("Missing Network Service folder. Expected at '%s'", ns_folder_abs_path)
            raise self._missing_ns_descriptor

        self.logger.debug('vNSFO package: %s', os.listdir(ns_folder_abs_path))
        self.logger.debug('NSD path: %s', nsd_file)

        # The Network Service Descriptor must be in the expected location so it's contents can be retrieved.
        nsd_file_abs_path = os.path.join(extracted_package_path, nsd_file)
        if not os.path.isfile(nsd_file_abs_path):
            self.logger.error("Missing NSD. Expected at '%s'", nsd_file)
            raise self._missing_ns_descriptor
        with open(nsd_file_abs_path, 'r') as stream:
            nsd = stream.read()

        self.logger.debug('NSD\n%s', nsd)

        # Set the vNSF package data useful for the onboarding operation.
        package_data = {'descriptor': nsd}

        rmtree(extracted_package_path)

        return package_data
