import tarfile


def extract_package(tar_gz_file_path, extract_path):
    package = tarfile.open(tar_gz_file_path)
    package.extractall(extract_path)
    package.close()
