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
import yaml
from shutil import rmtree
from storeutils import tar_package
from storeutils.error_utils import ExceptionMessage_, IssueHandling, IssueElement
from tempfile import gettempdir, mkdtemp
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


class NsMissingPackage(ExceptionMessage_):
    """Network Service package not provided."""


class NsWrongPackageFormat(ExceptionMessage_):
    """Network Service package file is not in .tar.gz format."""


class NsPackageCompliance(ExceptionMessage_):
    """Network Service package contents do not comply with the definition."""


class NsHelper(object):
    errors = {
        'ONBOARD_NS': {
            'MISSING_PACKAGE': {
                IssueElement.ERROR.name: ['No package file provided in POST'],
                IssueElement.EXCEPTION.name: NsMissingPackage('No package provided')
                },
            'PKG_NOT_TARGZ': {
                IssueElement.ERROR.name: ['Package is not a valid .tar.gz file'],
                IssueElement.EXCEPTION.name: NsWrongPackageFormat('Package is not a valid .tar.gz file')
                },
            'PKG_NOT_SHIELD': {
                IssueElement.ERROR.name: ["Missing 'manifest.yaml' from {}", 'Package contents: {}'],
                IssueElement.EXCEPTION.name: NsPackageCompliance('Package does not comply with the SHIELD format')
                }
            }
        }

    def __init__(self, vnsfo, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.issue = IssueHandling(self.logger)

        self.vnsfo = vnsfo

    def onboard_ns(self, tenant_id, ns_package, validation_data):
        """
        Registers a Network Service into the Store and onboards it with the Orchestrator.

        The SHIELD manifest is checked for integrity and compliance. Metadata is stored for the catalogue and the actual
        manifest file is stored as binary so it can be provided for attestation purposes (thus ensuring
        tamper-proofing).

        :param tenant_id: the tenant identifier to onboard the Network Service.
        :param ns_package: the package to onboard (as files MultiDict field from
        http://werkzeug.pocoo.org/docs/0.12/wrappers/#werkzeug.wrappers.BaseRequest).

        :return:    the manifest file as a FileStorage stream (
        http://werkzeug.pocoo.org/docs/0.12/datastructures/#werkzeug.datastructures.FileStorage).
                    the package metadata as a dictionary.
        """

        self.logger.info("Onboard Network Service from package '%s'", ns_package.filename)

        # Ensure it's a SHIELD Network Service package.
        extracted_package_path, manifest_path = self._extract_package(ns_package)

        # Get the SHIELD manifest data.
        with open(manifest_path, 'r') as stream:
            manifest = dict(yaml.safe_load(stream))
            self.logger.debug('SHIELD manifest\n%s', manifest)

        self.logger.debug('shield package: %s', os.listdir(extracted_package_path))
        self.logger.debug('osm package: %s | path: %s', manifest['manifest:ns']['package'],
                          os.path.join(extracted_package_path, manifest['manifest:ns'][
                              'package']))

        # Gather the information data format
        data_format = manifest['manifest:ns']['type']

        # Onboard the Network Service into the actual Orchestrator.
        # NOTE: any exception raised by the vNSFO must be handled by the caller, hence no try/catch here.
        onboarded_package = self.vnsfo.onboard_ns(tenant_id,
                                                  os.path.join(extracted_package_path,
                                                               manifest['manifest:ns']['package']),
                                                  manifest['manifest:ns']['descriptor'],
                                                  data_format,
                                                  validation_data)

        # Provide the manifest as a file stream.
        stream = open(manifest_path, 'rb')
        manifest_fs = FileStorage(stream)

        # Build the Network Service package metadata.
        package_data = dict()
        package_data['state'] = 'sandboxed'
        package_data['manifest'] = manifest
        package_data['descriptor'] = onboarded_package['descriptor']
        package_data['ns_id'] = onboarded_package['ns_id']
        package_data['constituent_vnsfs'] = onboarded_package['constituent_vnsfs']

        if os.path.isdir(extracted_package_path):
            rmtree(extracted_package_path)

        return manifest_fs, package_data

    def _extract_package(self, package_file):
        """
        Ensures the Network Service package is compliant. The package is stored locally so it's contents can be
        processed.

        :param package_file: The package to onboard (as files MultiDict field from
        http://werkzeug.pocoo.org/docs/0.12/wrappers/#werkzeug.wrappers.BaseRequest).

        :return:  extracted package absolute file system path;
                  SHIELD manifest absolute file system path.
        """

        if package_file and package_file.filename == '':
            self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['MISSING_PACKAGE'])

        filename = secure_filename(package_file.filename)
        package_absolute_path = os.path.join(gettempdir(), filename)

        try:
            package_file.save(package_absolute_path)

            if not tar_package.is_tar_gz_file(package_absolute_path):
                self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['PKG_NOT_TARGZ'])

            self.logger.debug("Package stored at '%s'", package_absolute_path)

            extracted_package_path = mkdtemp()

            tar_package.extract_package(package_absolute_path, extracted_package_path)

            # Get the SHIELD manifest data.
            manifest_path = os.path.join(extracted_package_path, 'manifest.yaml')
            if not os.path.isfile(manifest_path):
                self.issue.raise_ex(IssueElement.ERROR, self.errors['ONBOARD_NS']['PKG_NOT_SHIELD'],
                                    [[extracted_package_path], [os.listdir(extracted_package_path)]])

        finally:
            os.remove(package_absolute_path)

        return extracted_package_path, manifest_path
