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


import os
import tarfile


def extract_package(tar_gz_file_path, extract_path):
    package = tarfile.open(tar_gz_file_path)
    package.extractall(extract_path)
    package.close()


def is_tar_gz_file(file_path):
    """
    Ensures a file is an actual .tar.gz file and can be used as such.

    :param file_path: the file system path to where the .tar.gz file is.
    :return: whether it is a .tar.gz.
    """

    # It must be a .tar file.
    if not tarfile.is_tarfile(file_path):
        return False

    # Ensure it is a .tar.gz file.
    try:
        tarfile.open(file_path, "r:gz")
    except tarfile.ReadError:
        return False

    return True


def get_tar_gz_basename(file_path):
    """
    Extracts the .tar.gz file name from a file path. It assumes the file path ends with '.tar.gz' and doesn't enforce
    this for performance sake.

    :param file_path: the file name (may include path) ending with .tar.gz extension to extract the basename from.

    :return: the .tar.gz basename.
    """
    return os.path.splitext(os.path.basename(file_path))[0].replace('.tar', '')


class ExceptionMessage(Exception):
    def __init__(self, message):
        self.message = message
        super(ExceptionMessage, self).__init__(message)
