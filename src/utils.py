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
