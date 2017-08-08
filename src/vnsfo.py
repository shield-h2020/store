import logging

import os
import requests
import shutil
import tarfile
import tempfile

import store_errors as err


class VnsfoVnsfWrongPackageFormat(Exception):
    pass


class VnsfoMissingVnsfDescriptor(Exception):
    pass


class VnsfOrchestratorOnboardingException(Exception):
    pass


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

        if port is not None:
            server += ':' + port

        self.basepath = '{}://{}/{}'.format(protocol, server, api_basepath)
        self.logger.info('vNSF Orchestrator API at: %s', self.basepath)

    def _parse_vnsf_package(self, vnsf_package_path, vnsfd_file):
        """
        Decompresses a vNSF package and looks for the expected files and content according to what the vNSF
        Orchestrator is expecting.

        :param vnsf_package_path: The file system path to the vNSF package (.tar.gz) file.
        :param vnsfd_file: The path to where the vNSF Descriptor file (<name>_vnfd.yaml) is located within the package.

        :return: The vNSF package data relevant to the onboarding operation.
        """

        # The vNSF package must be in the proper format (.tar.gz).
        if not tarfile.is_tarfile(vnsf_package_path):
            self.logger.error(err.PKG_NOT_TARGZ)
            raise VnsfoVnsfWrongPackageFormat(err.PKG_NOT_TARGZ)

        extracted_package_path = tempfile.mkdtemp()

        package = tarfile.open(vnsf_package_path)
        package.extractall(extracted_package_path)
        package.close()

        self.logger.debug('extracted package path: %s', extracted_package_path)
        self.logger.debug('extracted contents: %s', os.listdir(extracted_package_path))
        self.logger.debug('vNSFO package: %s',
                          os.listdir(os.path.join(extracted_package_path, os.listdir(extracted_package_path)[0])))
        self.logger.debug('vnsfd_path: %s', vnsfd_file)

        # The vNSF Descriptor must be in the expected location so it's contents can be retrieved.
        vnfd_file_abs_path = os.path.join(extracted_package_path, vnsfd_file)
        if not os.path.isfile(vnfd_file_abs_path):
            self.logger.error("Missing vNSFD. Expected at '%s'", vnsfd_file)
            raise VnsfoMissingVnsfDescriptor(err.PKG_MISSING_VNSFD)
        with open(vnfd_file_abs_path, 'r') as stream:
            vnsfd = stream.read()

        # Set the vNSF package data useful for the onboarding operation.
        package_data = dict()
        package_data['descriptor'] = vnsfd

        self.logger.debug('vNSFD\n%s', vnsfd)

        shutil.rmtree(extracted_package_path)

        return package_data

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
        :return:
        """

        # Extract the vNSF package details relevant for onboarding.
        package = self._parse_vnsf_package(vnsf_package_path, vnsfd_file)

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
            r.status_code == 200 or VnsfOrchestratorOnboardingException('Can not onboard vNSF')
        except requests.exceptions.ConnectionError:
            self.logger.error('Error onboarding the vNSF at %s', url)
            raise VnsfOrchestratorOnboardingException('Can not reach the Orquestrator')

        return package
