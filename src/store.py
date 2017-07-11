# -*- coding: utf-8 -*-

import json

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

port = int(os.environ.get('API_PORT', 5000))

# use '0.0.0.0' to ensure your REST API is reachable from all your
# network (and not only your computer).
host = '0.0.0.0'


def onboard(request):
    # print(request.form)
    # print('files: {}'.format(request.files))

    # TODO Define proper response codes according to errors.
    if 'package' not in request.files:
        abort(401)

    file = request.files['package']

    if file and file.filename == '':
        abort(402)

    filename = secure_filename(file.filename)
    package_absolute_path = os.path.join(tempfile.gettempdir(), filename)

    extracted_package_path = ''

    try:
        file.save(package_absolute_path)

        if not tarfile.is_tarfile(package_absolute_path):
            file.remove()
            abort(403)

        extracted_package_path = tempfile.mkdtemp()

        package = tarfile.open(package_absolute_path)
        package.extractall(extracted_package_path)
        package.close()

        stream = open(os.path.join(extracted_package_path, 'manifest.yaml'), 'r')
        manifest = dict(yaml.load(stream))
        stream.close()

        print(manifest)

        # TODO Ensure the file name is secure. secure_filename() removes the / characters which isn't nice
        desciptor_file = manifest['manifest:vnsf']['descriptor']
        stream = open(os.path.join(extracted_package_path, desciptor_file), 'r')
        descriptor = stream.read()
        stream.close()

        stream = open(os.path.join(extracted_package_path, 'manifest.yaml'), 'rb')
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
    finally:
        os.remove(package_absolute_path)
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

    payload_json = json.loads(response.get_data(as_text=True))
    response.set_data(base64.b64decode(payload_json['manifest_file']))

    response.headers['Content-Disposition'] = 'attachment;filename=a.zip'
    response.headers['Content-Type'] = 'application/octet-stream'


app = Eve()
app.on_pre_POST_vnsfs += onboard
app.on_fetched_item_vnsfs += send_minimal_vnsf_data
app.on_post_GET_attestation += send_attestation

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
