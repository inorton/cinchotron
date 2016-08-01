"""
Wrappers around tempfile.mkdtemp()
"""
import os
import tempfile
import shutil
from contextlib import contextmanager


@contextmanager
def gashdir(prefix):
    """
    Create a temp folder and clean it up.
    :param prefix:
    :return:
    """
    path = tempfile.mkdtemp(prefix=prefix + os.sep)
    try:
        yield path
    finally:
        shutil.rmtree(path)
