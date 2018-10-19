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

import flask
import os
import requests
import yaml
from eve.methods.get import get_internal
from shutil import rmtree
from storeutils import http_utils, tar_package
from storeutils.error_utils import IssueHandling, IssueElement
from tempfile import mkdtemp

from .vnsfo_adapter import VnsfOrchestratorAdapter


class OsmVnsfoAdapter(VnsfOrchestratorAdapter):
    """
    Open Source Mano Orchestrator adapter.
    """

    def __init__(self, protocol, server, port, api_basepath, logger=None):
        super().__init__(protocol, server, port, api_basepath, logger)
        self.logger = logger or logging.getLogger(__name__)
        self.issue = IssueHandling(self.logger)

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
                self.issue.raise_ex(IssueElement.ERROR, self.errors['POLICY']['POLICY_ISSUE'],
                                    [[url, r.status_code]])

        except requests.exceptions.ConnectionError:
            self.issue.raise_ex(IssueElement.ERROR, self.errors['POLICY']['VNSFO_UNREACHABLE'],
                                [[url]])

    def onboard_vnsf(self, tenant_id, vnsf_package_path, vnsfd_file, data_format, validation_data):
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
        package_data = self._parse_vnsf_package(vnsf_package_path, vnsfd_file, data_format, validation_data)

        self.logger.debug("package data: %s", package_data)

        url = '{}/package/onboard'.format(self.basepath)

        # 'Content-Type': 'multipart/form-data' is set by the requests library.
        files = {'package': (os.path.split(vnsf_package_path)[1], open(vnsf_package_path, 'rb'))}

        self.logger.debug("Onboard vNSF package '%s' to '%s'", vnsf_package_path, url)

        try:
            r = requests.post(url, files=files, verify=False)

            if len(r.text) > 0:
                self.logger.debug(r.text)

            if not r.status_code == http_utils.HTTP_202_ACCEPTED:
                self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_VNSF']['ONBOARDING_ISSUE'],
                                    [[url, r.reason, r.status_code]])

        except requests.exceptions.ConnectionError:
            self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_VNSF']['VNSFO_UNREACHABLE'],
                                [[url]])

        return package_data

    def delete_vnsf(self, tenant_id, vnsf_id):
        """
        Delete a nNSF from the Orchestrator
        :param ns_id: The vNSF ID
        :return:
        """

        url = '{}/package/{}'.format(self.basepath, vnsf_id)
        headers = {'Content-Type': 'application/json'}
        self.logger.debug("Delete vNSF '{}' from Orchestrator".format(vnsf_id))
        try:
            r = requests.delete(url, headers=headers, verify=False)
            if not r.status_code == http_utils.HTTP_200_OK or not r.status_code == http_utils.HTTP_202_ACCEPTED:
                self.issue.raise_ex(IssueElement.ERROR, self.errors['DELETE_VNSF']['DELETING_ISSUE'],
                                    [[url, r.reason, r.status_code]])
        except requests.exceptions.ConnectionError:
            self.issue.raise_ex(IssueElement.ERROR, self.errors['DELETE_VNSF']['VNSFO_UNREACHABLE'], [[url]])

    def _parse_vnsf_package(self, vnf_package_path, vnfd_file, data_format, validation_data):
        """
        Decompresses a vNF package and looks for the expected files and content according to what the vNSF
        Orchestrator is expecting.

        :param vnf_package_path: The file system path to the vNSF package (.tar.gz) file.
        :param vnfd_file: The path to where the vNSF Descriptor file (<name>_vnfd.yaml) is located within the package.

        :return: The vNSF package data relevant to the onboarding operation.
        """

        # The vNSF package must be in '.tar.gz' format.
        if not tar_package.is_tar_gz_file(vnf_package_path):
            self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_VNSF']['VNSFPKG_NOT_VNSFO'])

        extracted_package_path = mkdtemp()

        tar_package.extract_package(vnf_package_path, extracted_package_path)

        self.logger.debug('extracted package path: %s', extracted_package_path)
        self.logger.debug('extracted contents: %s', os.listdir(extracted_package_path))
        self.logger.debug('package data format: %s', data_format)

        # The vNF package folder must exist. The folder name is the same as the VNF package one with .tar.gz removed.
        vnf_folder_abs_path = os.path.join(extracted_package_path, tar_package.get_tar_gz_basename(vnf_package_path))
        if not os.path.isdir(vnf_folder_abs_path):
            self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_VNSF']['PKG_MISSING_VNFD_FOLDER'],
                                [[vnf_folder_abs_path]])

        self.logger.debug('vNSFO package: %s', os.listdir(vnf_folder_abs_path))
        self.logger.debug('VNFD path: %s', vnfd_file)

        # The vNSF Descriptor must be in the expected location so it's contents can be retrieved.
        vnfd_file_abs_path = os.path.join(extracted_package_path, vnfd_file)
        if not os.path.isfile(vnfd_file_abs_path):
            self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_VNSF']['PKG_MISSING_VNFD'],
                                [[vnfd_file]])

        vnsfd = None
        with open(vnfd_file_abs_path, 'r') as stream:
            try:
                vnsfd = yaml.load(stream)

            except yaml.YAMLError:
                self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_VNSF']['VNFD_FORMAT_INVALID'],
                                    [[vnfd_file]])

        self.logger.debug('VNFD\n%s', vnsfd)

        # # Validate vNSF Descriptor using NSFVal
        # if data_format == "OSM-R2":
        #     val_result = nsfval.validate_vnf('osm-r2', 'sit', vnfd_file_abs_path)
        # elif data_format == 'OSM-R4':
        #     val_result = nsfval.validate_vnf('osm-r4', 'sit', vnfd_file_abs_path)
        # else:
        #     val_result = nsfval.validate_vnf('osm-r4', 'sit', vnfd_file_abs_path)
        #
        # # Build the validation data structure
        # validation_data.update(val_result)
        # validation_data['type'] = 'vNSF'
        #
        # # Raise exception if validation errors were found.
        # if validation_data['result']['error_count'] != 0:
        #     self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_VNSF']['VALIDATION_ERROR'], [[vnfd_file]])
        # self.logger.debug("vNSF descriptor '%s' validation PASS", vnfd_file)

        # Retrieve VNF ID
        vnsf_id = vnsfd[list(vnsfd.keys())[0]]['vnfd'][0]['id']

        # Set the vNSF package data useful for the onboarding operation.
        package_data = {
            'vnsf_id':    str(vnsf_id),  # assuming the descriptor only carries one VNFD
            'descriptor': str(vnsfd)
            }

        rmtree(extracted_package_path)

        return package_data

    def onboard_ns(self, tenant_id, ns_package_path, nsd_file, data_format, validation_data):
        """
        Onboards a NS with the Orchestrator.

        :param tenant_id: The tenant where to onboard the Network Service.
        :param ns_package_path: The file system path where the Network Service package is stored.
        :param nsd_file: The relative path to the Network Service Descriptor within the package.

        :return: the Network Service package data.
        """

        # Extract the Network Service package details relevant for onboarding.
        package_data = self._parse_ns_package(ns_package_path, nsd_file, data_format, validation_data)

        self.logger.debug("package data: %s", package_data)

        url = '{}/package/onboard'.format(self.basepath)

        files = {'package': (os.path.split(ns_package_path)[1], open(ns_package_path, 'rb'))}

        self.logger.debug("Onboard Network Service package '%s' to '%s'", ns_package_path, url)

        try:
            r = requests.post(url, files=files, verify=False)

            if len(r.text) > 0:
                self.logger.debug(r.text)

            if not r.status_code == http_utils.HTTP_202_ACCEPTED:
                self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['ONBOARDING_ISSUE'],
                                    [[url, r.reason, r.status_code]])

        except requests.exceptions.ConnectionError:
            self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['VNSFO_UNREACHABLE'],
                                [[url]])

        return package_data

    def delete_ns(self, tenant_id, ns_id):
        """
        Delete a NS from the Orchestrator
        :param ns_id: The Network Service ID
        :return:
        """

        url = '{}/package/{}'.format(self.basepath, ns_id)
        headers = {'Content-Type': 'application/json'}
        self.logger.debug("Delete Network Service '{}' from Orchestrator".format(ns_id))
        try:
            r = requests.delete(url, headers=headers, verify=False)
            if not r.status_code == http_utils.HTTP_200_OK or not r.status_code == http_utils.HTTP_202_ACCEPTED:
                self.issue.raise_ex(IssueElement.ERROR, self.errors['DELETE_NS']['DELETING_ISSUE'],
                                    [[url, r.reason, r.status_code]])
        except requests.exceptions.ConnectionError:
            self.issue.raise_ex(IssueElement.ERROR, self.errors['DELETE_NS']['VNSFO_UNREACHABLE'], [[url]])

    def _parse_ns_package(self, ns_package_path, nsd_file, data_format, validation_data):
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
            self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['NSPKG_NOT_VNSFO'])

        extracted_package_path = mkdtemp()

        tar_package.extract_package(ns_package_path, extracted_package_path)

        self.logger.debug('extracted package path: %s', extracted_package_path)
        self.logger.debug('extracted contents: %s', os.listdir(extracted_package_path))
        self.logger.debug('package data format: %s', data_format)

        # The Network Service package folder must exist. The folder name is the same as the Network Service package
        # one with .tar.gz removed.
        ns_folder_abs_path = os.path.join(extracted_package_path, tar_package.get_tar_gz_basename(ns_package_path))
        if not os.path.isdir(ns_folder_abs_path):
            self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['PKG_MISSING_NS_FOLDER'],
                                [[ns_folder_abs_path]])

        self.logger.debug('vNSFO package: %s', os.listdir(ns_folder_abs_path))
        self.logger.debug('NSD path: %s', nsd_file)

        # The Network Service Descriptor must be in the expected location so it's contents can be retrieved.
        nsd_file_abs_path = os.path.join(extracted_package_path, nsd_file)
        if not os.path.isfile(nsd_file_abs_path):
            self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['PKG_MISSING_NSD'],
                                [[nsd_file]])

        nsd = None
        with open(nsd_file_abs_path, 'r') as stream:
            try:
                nsd = yaml.load(stream)

            except yaml.YAMLError:
                self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['NSD_FORMAT_INVALID'],
                                    [[nsd_file]])

        self.logger.debug('NSD\n%s', nsd)

        # Retrieve nsd inner content
        nsd_inner = nsd[list(nsd.keys())[0]]['nsd'][0]

        # Retrieve NS ID
        ns_id = nsd_inner['id']
        ns_name = nsd_inner['name']

        # Retrieve vnsf dependencies
        vnsf_ids = list()
        for c_vnfd in nsd_inner['constituent-vnfd']:

            # check if NS descriptor is missing vnfd references
            if 'vnfd-id-ref' not in c_vnfd:
                self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['VALIDATION_ERROR'], [[nsd_file]])

            vnsf_ids.append(c_vnfd['vnfd-id-ref'])

        # Get stored vnsfs
        vnsfds = dict()
        constituent_vnsfs = list()
        app = flask.current_app
        for vnsf_id in vnsf_ids:
            payload = get_internal('vnsfs', vnsf_id=vnsf_id)[0]['_items']

            # Raise exception if couldn't get the dependent vNSF
            if not payload:
                self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['MISSING_VNSF_DEPENDENCY'],
                                    [[vnsf_id, ns_id]])

            payload = payload[0]
            vnsfds[vnsf_id] = payload['descriptor']

            # Associate this NS with its constituent vNSFs
            constituent_vnsfs.append(payload['_id'])

        # Persist vNSF descriptors to files
        vnsfd_files = list()
        for vnsf_id, vnsfd in vnsfds.items():

            # Load the string content as dict
            vnsfd_content = yaml.load(vnsfd)

            # Write the content to file
            filename = os.path.join(extracted_package_path, str(vnsf_id) + '.yaml')
            with open(filename, 'w') as _f:
                yaml.dump(vnsfd_content, _f, default_flow_style=False)

            vnsfd_files.append(filename)

        # # Validate NS Descriptor using NSFVal
        # if data_format == 'OSM-R2':
        #     val_result = nsfval.validate_ns('osm-r2', 'sit', nsd_file_abs_path, addt_files=vnsfd_files)
        # elif data_format == 'OSM-R4':
        #     val_result = nsfval.validate_ns('osm-r4', 'sit', nsd_file_abs_path, addt_files=vnsfd_files)
        # else:
        #     val_result = nsfval.validate_ns('osm-r4', 'sit', nsd_file_abs_path, addt_files=vnsfd_files)
        #
        # # Build the validation data structure
        # validation_data.update(val_result)
        # validation_data['type'] = 'NS'
        #
        # # Raise exception if validation errors were found.
        # if validation_data['result']['error_count'] != 0:
        #     self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['VALIDATION_ERROR'], [[nsd_file]])
        # self.logger.debug("NS descriptor '%s' validation PASS", nsd_file)

        # Set the vNSF package data useful for the onboarding operation.
        package_data = {
            'ns_id':             str(ns_id),  # assuming the descriptor only carries one NSD
            'ns_name':           str(ns_name),
            'descriptor':        str(nsd),
            'constituent_vnsfs': constituent_vnsfs
            }

        rmtree(extracted_package_path)
        return package_data
