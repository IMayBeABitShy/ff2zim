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


def format_size(nbytes):
    """
    Format the given byte count into a human readable format.
    
    @param nbytes: size in bytes
    @type nbytes: L{int}
    @return: a human readable string describing the size
    @rtype: L{str}
    """
    for fmt in ("B", "KiB", "MiB", "GiB", "TiB"):
        if nbytes < 1024.0:
            return "{:.2f} {}".format(round(nbytes, 2), fmt)
        else:
            nbytes /= 1024.0
    return "{:.2f} PiB".format(round(nbytes, 2))


def get_size_of(path, extensions=None):
    """
    Get the size of a specified path in bytes.
    
    If path points to a directory, the size will be recursively calculated.
    
    @param path: path to get size of
    @type path: L{str}
    @param extensions: if specified, only files with these extensions will be taken into account
    @return: the size of the path in bytes
    @rtype: L{str}
    """
    if not os.path.exists(path):
        return 0
    if os.path.isdir(path):
        s = 0
        for fn in os.listdir(path):
            fp = os.path.join(path, fn)
            s += get_size_of(fp, extensions=extensions)
        return s
    else:
        if extensions is not None:
            if os.path.splitext(path)[1] not in extensions:
                return 0
        return os.stat(path).st_size
