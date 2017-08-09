import logging

import os
import tarfile
import yaml
from shutil import rmtree
from tempfile import gettempdir, mkdtemp
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from werkzeug.utils import secure_filename

import settings as cfg
import store_errors as err
from utils import extract_package
from vnsfo import VnsfOrchestratorAdapter


class VnsfMissingPackage(Exception):
    pass


class VnsfWrongPackageFormat(Exception):
    pass


class VnsfPackageCompliance(Exception):
    pass


class Vnsf:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

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
            raise VnsfMissingPackage(err.PKG_MISSING_FILE)

        package_file = files['package']
        if package_file and package_file.filename == '':
            self.logger.info('No package file provided in POST')
            raise VnsfMissingPackage(err.PKG_MISSING_FILE)

        filename = secure_filename(package_file.filename)
        package_absolute_path = os.path.join(gettempdir(), filename)

        try:
            package_file.save(package_absolute_path)

            if not tarfile.is_tarfile(package_absolute_path):
                self.logger.error(err.PKG_NOT_TARGZ)
                raise VnsfWrongPackageFormat(err.PKG_NOT_TARGZ)

            self.logger.debug("Package stored at '%s'", package_absolute_path)

            extracted_package_path = mkdtemp()

            extract_package(package_absolute_path, extracted_package_path)

            # Get the SHIELD manifest data.
            manifest_path = os.path.join(extracted_package_path, 'manifest.yaml')
            if not os.path.isfile(manifest_path):
                self.logger.error("Missing 'manifest.yaml' from package")
                raise VnsfPackageCompliance(err.PKG_NOT_SHIELD)

        finally:
            os.remove(package_absolute_path)

        return extracted_package_path, manifest_path
