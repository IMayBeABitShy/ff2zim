"""
Utilities for common I/O operations.
"""
import os
import shutil

import requests

from .exceptions import AlreadyExists


DOWNLOAD_CHUNKSIZE = 8192
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"}


def download_file(url, path):
    """
    Download a file from an URL into the file at path.
    
    @param url: URL to download
    @type url: L{str}
    @param path: path to write to
    @type path: L{str}
    """
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(path, "wb") as fout:
        for chunk in r.iter_content(DOWNLOAD_CHUNKSIZE):
            fout.write(chunk)


def create_file_with_content(path, content):
    """
    Create a file with the specified content.
    
    @param path: path to write to
    @type path: L{str}
    @param content: content to write
    @type content: L{str}
    """
    if os.path.exists(path):
        raise AlreadyExists("Path '{}' already exists.".format(path))
    with open(path, "w") as fout:
        fout.write(content)


def append_to_file(path, content):
    """
    Append the specified content to the specified path.
    
    @param path: path to append to
    @type path: L{str}
    @param content: content to append
    @type content: L{str}
    """
    with open(path, "a") as fout:
        fout.write(content)


def copy_resource_file(name, dest):
    """
    Copy a resource file from the 'resource' subdirectory of the package to the specified path.

    @param name: name of the resource file to copy
    @type name: L{str}
    @param dest: path to copy to
    @type dest: L{str}
    """
    p = os.path.join(os.path.dirname(__file__), "resources", name)
    shutil.copyfile(p, dest)
