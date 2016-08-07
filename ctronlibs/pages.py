"""
Render various basic HTML pages
"""
import os
import cgi
import urllib
import posixpath
import re

class FileTypeGlyfs(object):
    """
    Silly class to get dir entry 'glyfs' based on their name
    """
    PLAINFILE = " " * 5

    def __init__(self):
        self.types = []

    def add(self, pattern, glyf):
        """
        Add a new glyf type matcher
        :param pattern: a re.Pattern we use to search
        :param glyf:
        :return:
        """
        self.types.append((glyf, pattern))

    def match(self, name):
        """
        Return the matching glyf
        :param name:
        :return:
        """
        for pair in self.types:
            glyf, pattern = pair
            if pattern.search(name):
                return glyf

        return FileTypeGlyfs.PLAINFILE

glyf_registry = FileTypeGlyfs()
glyf_registry.add(re.compile("/"), "[DIR]")
glyf_registry.add(re.compile("\.txt$"), "[TXT]")
glyf_registry.add(re.compile("\.log$"), "[TXT]")
glyf_registry.add(re.compile("\.htm[l]?$"), "[HTM]")


class IndexEntry(object):
    """
    An item in an index
    """
    def __init__(self, path, name, size=0):
        """
        An index entry
        :param path: The relative URL of this item
        :param name:
        :param size: Size in bytes
        :return:
        """
        self.path = path
        self.name = name
        self.size = size

    def glyf(self):
        """
        Return a simple string that might suggest the entry type
        :return:
        """
        return glyf_registry.match(self.name)


class IndexPage(object):
    """
    Render an Index.
    """

    def __init__(self, request):
        """
        Render an index page
        :param request: The CinchHTTPRequestHandler request
        :return:
        """
        self.displaypath = cgi.escape(urllib.unquote(request.path))
        self.localpath = request.translate_path(request.path)
        self.request = request

    def get_files(self):
        """
        Get the file items
        :return:
        """
        files = []
        for item in os.listdir(self.localpath):
            itempath = os.path.join(self.localpath, item)
            if os.path.isfile(itempath):
                files.append(IndexEntry(posixpath.join(self.request.path,
                                                       item)),
                             item, size=os.path.getsize(itempath))
        return files

    def get_folders(self):
        """
        Get the folder items
        :return:
        """
        folders = []
        for item in os.listdir(self.localpath):
            itempath = os.path.join(self.localpath, item)
            if os.path.isdir(itempath):
                folders.append(IndexEntry(posixpath.join(self.request.path,
                                                         item)),
                               item + "/")
        return folders
