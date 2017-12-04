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
import subprocess
import time

import os
import yaml
from shutil import rmtree
from tempfile import gettempdir, mkdtemp
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from werkzeug.utils import secure_filename

import settings as cfg
import store_errors as err
import utils
from vnsfo import VnsfOrchestratorAdapter


class VnsfMissingPackage(utils.ExceptionMessage):
    """vNSF package not provided."""


class VnsfWrongPackageFormat(utils.ExceptionMessage):
    """vNSF package file is not in .tar.gz format."""


class VnsfPackageCompliance(utils.ExceptionMessage):
    """vNSF package contents do not comply with the definition."""


class Vnsf:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

        # Maintenance friendly.
        self._missing_package = VnsfMissingPackage(err.PKG_MISSING_FILE)
        self._wrong_package_format = VnsfWrongPackageFormat(err.PKG_NOT_TARGZ)
        self._package_compliance = VnsfPackageCompliance(err.PKG_NOT_SHIELD)

    def onboard_vnsf(self, request):
        """
        Registers a vNSF into the Store and onboards it with the Orchestrator.

        The SHIELD manifest is checked for integrity and compliance. Metadata is stored for the catalogue and the actual
        manifest file is stored as binary so it can be provided for attestation purposes (thus ensuring
        tamper-proofing).

        :param request: the HTTP request data.
        """

        self.logger.info("Onboard vNSF from package '%s'", request.files['package'].filename)

        # Ensure it's a SHIELD vNSF package.
        extracted_package_path, manifest_path = self._lint_vnsf_package(request.files)

        # Get the SHIELD manifest data.
        with open(manifest_path, 'r') as stream:
            manifest = dict(yaml.safe_load(stream))
            self.logger.debug('SHIELD manifest\n%s', manifest)

        self.logger.debug('shield package: %s', os.listdir(extracted_package_path))
        self.logger.debug('osm package: %s | path: %s', manifest['manifest:vnsf']['package'],
                          os.path.join(extracted_package_path, manifest['manifest:vnsf']['package']))

        # Onboard the VNF into the actual Orchestrator.
        vnsfo = VnsfOrchestratorAdapter(cfg.VNSFO_PROTOCOL, cfg.VNSFO_HOST, cfg.VNSFO_PORT, cfg.VNSFO_API)
        vnsf_package = vnsfo.onboard_vnsf(cfg.VNSFO_TENANT_ID,
                                          os.path.join(extracted_package_path,
                                                       manifest['manifest:vnsf']['package']),
                                          manifest['manifest:vnsf']['descriptor'])

        # Ensure the SHIELD manifest is stored as a binary file.
        # NOTE: the file is closed by Eve once stored.
        stream = open(manifest_path, 'rb')
        fs = FileStorage(stream)
        files = request.files.copy()
        files['manifest_file'] = fs
        request.files = ImmutableMultiDict(files)

        # Convert the vNSF package into the document data.
        # NOTE: there's no need to deep copy as the data won't be modified until it gets stored in the database.
        package_data = request.form.copy()
        package_data['registry'] = {'vendor': "vNSF maker A", 'capabilities': ["some stuff"]}
        package_data['state'] = 'sandboxed'
        package_data['manifest'] = manifest
        package_data['descriptor'] = vnsf_package['descriptor']
        request.form = ImmutableMultiDict(package_data)

        if os.path.isdir(extracted_package_path):
            rmtree(extracted_package_path)

        # Hack for Y1 demo.
        time.sleep(8)
        subprocess.call(['/usr/bin/python3', '/opt/shield/review/y1/packages/onboard_ns_package.py'])

    def _lint_vnsf_package(self, files):
        """
        Ensures the vNSF package is compliant. The package is stored locally so it's contents can be processed.

        :param files: The packages to onboard (as files MultiDict field from
        http://werkzeug.pocoo.org/docs/0.12/wrappers/#werkzeug.wrappers.BaseRequest).

        :return:  extracted package absolute file system path;
                  SHIELD manifest absolute file system path.
        """

        if 'package' not in files:
            self.logger.error("Missing or wrong field in POST. 'package' should be used as the field name")
            raise self._missing_package

        package_file = files['package']
        if package_file and package_file.filename == '':
            self.logger.info('No package file provided in POST')
            raise self._missing_package

        filename = secure_filename(package_file.filename)
        package_absolute_path = os.path.join(gettempdir(), filename)

        try:
            package_file.save(package_absolute_path)

            if not utils.is_tar_gz_file(package_absolute_path):
                self.logger.error(err.PKG_NOT_TARGZ)
                raise self._wrong_package_format

            self.logger.debug("Package stored at '%s'", package_absolute_path)

            extracted_package_path = mkdtemp()

            utils.extract_package(package_absolute_path, extracted_package_path)

            # Get the SHIELD manifest data.
            manifest_path = os.path.join(extracted_package_path, 'manifest.yaml')
            if not os.path.isfile(manifest_path):
                self.logger.error("Missing 'manifest.yaml' from %s", extracted_package_path)
                self.logger.error('Package contents: %s', os.listdir(extracted_package_path))
                raise self._package_compliance

        finally:
            os.remove(package_absolute_path)

        return extracted_package_path, manifest_path