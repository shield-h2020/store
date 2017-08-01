# -*- coding: utf-8 -*-


import json
import logging

import base64
import os
import shutil
import tarfile
import tempfile
import yaml
from eve import Eve
from flask import abort
from werkzeug.datastructures import FileStorage, ImmutableMultiDict
from werkzeug.utils import secure_filename

import log
import settings as cfg
import store_errors as err
from vnsfo import VnsfOrchestratorApi


def onboard(request):
    if 'package' not in request.files:
        logger.error('Missing <package> field in POST')
        abort(err.HTTP_412_PRECONDITION_FAILED, err.PKG_MISSING_FILE)

    file = request.files['package']

    if file and file.filename == '':
        logger.info('No package file provided in POST')
        abort(err.HTTP_412_PRECONDITION_FAILED, err.PKG_MISSING_FILE)

    filename = secure_filename(file.filename)
    package_absolute_path = os.path.join(tempfile.gettempdir(), filename)

    logger.info("Onboard vNSF from package '{}' stored at '{}'".format(file.filename, package_absolute_path))

    extracted_package_path = ''

    try:
        file.save(package_absolute_path)

        if not tarfile.is_tarfile(package_absolute_path):
            logger.error(err.PKG_NOT_TARGZ)
            abort(err.HTTP_412_PRECONDITION_FAILED, err.PKG_NOT_TARGZ)

        extracted_package_path = tempfile.mkdtemp()

        package = tarfile.open(package_absolute_path)
        package.extractall(extracted_package_path)
        package.close()

        manifest_path = os.path.join(extracted_package_path, 'manifest.yaml')
        if not os.path.isfile(manifest_path):
            logger.error("Missing 'manifest.yaml' from package")
            abort(err.HTTP_406_NOT_ACCEPTABLE, err.PKG_NOT_SHIELD)
        stream = open(manifest_path, 'r')
        manifest = dict(yaml.load(stream))
        stream.close()

        print(manifest)

        # TODO Ensure the file name is secure. secure_filename() removes the / characters which isn't nice
        desciptor_file = manifest['manifest:vnsf']['descriptor']
        stream = open(os.path.join(extracted_package_path, desciptor_file), 'r')
        descriptor = stream.read()
        stream.close()

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
        package_data['descriptor'] = descriptor
        request.form = ImmutableMultiDict(package_data)

        # Onboard the vNSF with the Orchestrator.
        vnsfo = VnsfOrchestratorApi(cfg.VNSFO_HOST, cfg.VNSFO_PORT, cfg.VNSFO_API)  # , logger)
        if not vnsfo.onboard_vnsf(cfg.TENANT_ID, package_absolute_path):
            logger.error('vNSF not onboarded with the Orchestrator')
            abort(err.HTTP_502_BAD_GATEWAY, err.VNSF_NOT_ADDED_TO_CATALOG)

    finally:
        os.remove(package_absolute_path)
        if os.path.isdir(extracted_package_path):
            shutil.rmtree(extracted_package_path)


def send_minimal_vnsf_data(response):
    """
    Send the vNSF attestation-related data.

    :param response: the response from the DB
    :return: The vNSF with the "public" properties only.
    """

    del response['manifest_file']
    del response['state']


def send_attestation(request, response):
    """
    Send the vNSF attestation-related data.

    :param request: the actual request
    :param response: the response from the DB
    :return: The attestation data.
    """

    logger.info('Send attestation data only')

    payload_json = json.loads(response.get_data(as_text=True))
    response.set_data(base64.b64decode(payload_json['manifest_file']))

    response.headers['Content-Disposition'] = 'attachment;filename=a.zip'
    response.headers['Content-Type'] = 'application/octet-stream'


app = Eve()
app.on_pre_POST_vnsfs += onboard
app.on_fetched_item_vnsfs += send_minimal_vnsf_data
app.on_post_GET_attestation += send_attestation

if __name__ == '__main__':
    log.setup_logging()
    logger = logging.getLogger(__name__)

    # use '0.0.0.0' to ensure your REST API is reachable from all your
    # network (and not only your computer).
    app.run(host='0.0.0.0', port=cfg.API_PORT, debug=True)
