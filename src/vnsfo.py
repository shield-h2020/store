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

import os
import requests
from shutil import rmtree
from tempfile import mkdtemp

import store_errors as err
import utils


class VnsfoVnsfWrongPackageFormat(utils.ExceptionMessage):
    """Wrong vNSFO package format."""


class VnsfoMissingVnfDescriptor(utils.ExceptionMessage):
    """Missing vNSF Descriptor from the package."""


class VnsfOrchestratorOnboardingIssue(utils.ExceptionMessage):
    """vNSFO onboarding operation failed."""


class VnsfOrchestratorAdapter:
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
        self._wrong_package_format = VnsfoVnsfWrongPackageFormat(err.PKG_NOT_VNSFO)
        self._missing_vnf_descriptor = VnsfoMissingVnfDescriptor(err.PKG_MISSING_VNFD)
        self._onboarding_issue = VnsfOrchestratorOnboardingIssue('Can not onboard vNSF into the vNFSO')
        self._unreachable = VnsfOrchestratorOnboardingIssue('Can not reach the Orquestrator')

        if port is not None:
            server += ':' + port

        self.basepath = '{}://{}/{}'.format(protocol, server, api_basepath)
        self.logger.debug('vNSF Orchestrator API at: %s', self.basepath)

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

        :return: the VNF package data.
        """

        # Extract the vNSF package details relevant for onboarding.
        package = self._parse_vnf_package(vnsf_package_path, vnsfd_file)

        self.logger.debug("package data: %s", package)

        url = '{}/upload?api_server=https://localhost'.format(self.basepath)

        # 'Content-Type': 'multipart/form-data' is set by the requests library.
        headers = {'Authorization': 'Basic YWRtaW46YWRtaW4='}

        files = {'package': (os.path.split(vnsf_package_path)[1], open(vnsf_package_path, 'rb'))}

        self.logger.debug("Onboard vNSF package '%s' to '%s'", vnsf_package_path, url)

        try:
            r = requests.post(url, headers=headers, files=files, verify=False)

            if len(r.text) > 0:
                self.logger.debug(r.text)

            if not r.status_code == 200:
                self.logger.error('vNFSO onboarding at {}. Status: {}'.format(url, r.status_code))
                raise self._onboarding_issue

        except requests.exceptions.ConnectionError:
            self.logger.error('Error onboarding the vNSF at %s', url)
            raise self._unreachable

        return package

    def _parse_vnf_package(self, vnf_package_path, vnfd_file):
        """
        Decompresses a vNF package and looks for the expected files and content according to what the vNSF
        Orchestrator is expecting.

        :param vnf_package_path: The file system path to the vNSF package (.tar.gz) file.
        :param vnfd_file: The path to where the vNSF Descriptor file (<name>_vnfd.yaml) is located within the package.

        :return: The vNSF package data relevant to the onboarding operation.
        """

        # The vNSF package must be in the proper format (.tar.gz).
        if not utils.is_tar_gz_file(vnf_package_path):
            self.logger.error(err.PKG_NOT_VNSFO)
            raise self._wrong_package_format

        extracted_package_path = mkdtemp()

        utils.extract_package(vnf_package_path, extracted_package_path)

        self.logger.debug('extracted package path: %s', extracted_package_path)
        self.logger.debug('extracted contents: %s', os.listdir(extracted_package_path))

        # The vNF package folder must exist. The folder name is the same as the VNF package one with .tar.gz removed.
        vnf_folder_abs_path = os.path.join(extracted_package_path, utils.get_tar_gz_basename(vnf_package_path))
        if not os.path.isdir(vnf_folder_abs_path):
            self.logger.error("Missing VNF folder. Expected at '%s'", vnf_folder_abs_path)
            raise self._missing_vnf_descriptor

        self.logger.debug('vNSFO package: %s', os.listdir(vnf_folder_abs_path))
        self.logger.debug('VNFD path: %s', vnfd_file)

        # The vNSF Descriptor must be in the expected location so it's contents can be retrieved.
        vnfd_file_abs_path = os.path.join(extracted_package_path, vnfd_file)
        if not os.path.isfile(vnfd_file_abs_path):
            self.logger.error("Missing VNFD. Expected at '%s'", vnfd_file)
            raise self._missing_vnf_descriptor
        with open(vnfd_file_abs_path, 'r') as stream:
            vnsfd = stream.read()

        self.logger.debug('VNFD\n%s', vnsfd)

        # Set the vNSF package data useful for the onboarding operation.
        package_data = {'descriptor': vnsfd}

        rmtree(extracted_package_path)

        return package_data
