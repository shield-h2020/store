import logging

import os
import shutil
import tarfile
import tempfile
import yaml
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from werkzeug.utils import secure_filename

import settings as cfg
import store_errors as err
from vnsfo import VnsfOrchestratorAdapter, VnsfOrchestratorOnboardingException


class VnsfMissingPackage(Exception):
    pass


class VnsfWrongPackageCompression(Exception):
    pass


class VnsfPackageCompliance(Exception):
    pass


class VnsfMissingDescriptor(Exception):
    pass


class VnsfOrchestratorIssue(Exception):
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

        if 'package' not in request.files:
            self.logger.error('Missing <package> field in POST')
            raise VnsfMissingPackage(err.PKG_MISSING_FILE)

        file = request.files['package']

        if file and file.filename == '':
            self.logger.info('No package file provided in POST')
            raise VnsfMissingPackage(err.PKG_MISSING_FILE)

        filename = secure_filename(file.filename)
        package_absolute_path = os.path.join(tempfile.gettempdir(), filename)

        self.logger.info("Onboard vNSF from package '{}' stored at '{}'".format(file.filename, package_absolute_path))

        extracted_package_path = ''

        try:
            file.save(package_absolute_path)

            if not tarfile.is_tarfile(package_absolute_path):
                self.logger.error(err.PKG_NOT_TARGZ)
                raise VnsfWrongPackageCompression(err.PKG_NOT_TARGZ)

            extracted_package_path = tempfile.mkdtemp()

            package = tarfile.open(package_absolute_path)
            package.extractall(extracted_package_path)
            package.close()

            # Get SHIELD manifest data.
            manifest_path = os.path.join(extracted_package_path, 'manifest.yaml')
            if not os.path.isfile(manifest_path):
                self.logger.error("Missing 'manifest.yaml' from package")
                raise VnsfPackageCompliance(err.PKG_NOT_SHIELD)
            with open(manifest_path, 'r') as stream:
                manifest = dict(yaml.load(stream))
                self.logger.debug(manifest)

            # Get the vNSF Descriptor data.
            # TODO Ensure the file name is secure. secure_filename() removes the / characters which isn't nice
            vnfd_file = manifest['manifest:vnsf']['descriptor']
            vnfd_path = os.path.join(extracted_package_path, vnfd_file)
            if not os.path.isfile(vnfd_path):
                self.logger.error("Missing vNSFD. Expected at '{}'".format(vnfd_file))
                raise VnsfMissingDescriptor(err.PKG_MISSING_VNSFD)
            with open(vnfd_path, 'r') as stream:
                vnfd = stream.read()

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
            package_data['descriptor'] = vnfd
            request.form = ImmutableMultiDict(package_data)

            # Onboard the vNSF with the Orchestrator.
            try:
                vnsfo = VnsfOrchestratorAdapter(cfg.VNSFO_PROTOCOL, cfg.VNSFO_HOST, cfg.VNSFO_PORT, cfg.VNSFO_API)
                vnsfo.onboard_vnsf(cfg.VNSFO_TENANT_ID, package_absolute_path)
            except VnsfOrchestratorOnboardingException:
                self.logger.error('vNSF not onboarded with the Orchestrator')
                raise VnsfOrchestratorIssue(err.VNSF_NOT_ADDED_TO_CATALOG)

        finally:
            os.remove(package_absolute_path)
            if os.path.isdir(extracted_package_path):
                shutil.rmtree(extracted_package_path)

    def onboard_vnsf__new(self, request):
        """
        Registers a vNSF into the Store and onboards it with the Orchestrator.

        The SHIELD manifest is checked for integrity and compliance. Metadata is stored for the catalogue and the actual
        manifest file is stored as binary so it can be provided for attestation purposes (thus ensuring
        tamper-proofing).

        :param request: the HTTP request data.
        """

        if 'package' not in request.files:
            self.logger.error('Missing <package> field in POST')
            raise VnsfMissingPackage(err.PKG_MISSING_FILE)

        file = request.files['package']

        if file and file.filename == '':
            self.logger.info('No package file provided in POST')
            raise VnsfMissingPackage(err.PKG_MISSING_FILE)

        filename = secure_filename(file.filename)
        package_absolute_path = os.path.join(tempfile.gettempdir(), filename)

        self.logger.info("Onboard vNSF from package '%s'", file.filename)
        self.logger.debug("Package stored at '%s'", package_absolute_path)

        extracted_package_path = ''

        try:
            file.save(package_absolute_path)

            if not tarfile.is_tarfile(package_absolute_path):
                self.logger.error(err.PKG_NOT_TARGZ)
                raise VnsfWrongPackageCompression(err.PKG_NOT_TARGZ)

            extracted_package_path = tempfile.mkdtemp()

            package = tarfile.open(package_absolute_path)
            package.extractall(extracted_package_path)
            package.close()

            # Get SHIELD manifest data.
            manifest_path = os.path.join(extracted_package_path, 'manifest.yaml')
            if not os.path.isfile(manifest_path):
                self.logger.error("Missing 'manifest.yaml' from package")
                raise VnsfPackageCompliance(err.PKG_NOT_SHIELD)
            with open(manifest_path, 'r') as stream:
                manifest = dict(yaml.load(stream))
                self.logger.debug(manifest)

            self.logger.info('shield: %s', os.listdir(extracted_package_path))
            self.logger.info('osm: %s', manifest['manifest:vnsf']['package'])
            self.logger.info('path: %s', os.path.join(extracted_package_path, manifest['manifest:vnsf']['package']))

            vnsfo = VnsfOrchestratorAdapter(cfg.VNSFO_PROTOCOL, cfg.VNSFO_HOST, cfg.VNSFO_PORT, cfg.VNSFO_API)
            vnsf_package = vnsfo.onboard_vnsf(cfg.VNSFO_TENANT_ID,
                               os.path.join(extracted_package_path, manifest['manifest:vnsf']['package']),
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

        finally:
            os.remove(package_absolute_path)
            if os.path.isdir(extracted_package_path):
                shutil.rmtree(extracted_package_path)
