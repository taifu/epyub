# -*- coding: utf-8 -*-

import os.path
import re
from zipfile import ZipFile
import xml.dom.minidom

from epyub.exceptions import *

TOC_NAME = "toc.ncx"
CONTENT_NAME = "content.opf"
CONTAINER_NAME = "container.xml"
MIMETYPE_NAME = "mimetype"

class Toc(object):
    def __init__(self, data):
        self._dom = xml.dom.minidom.parseString(data)

class Content(object):
    def __init__(self, data):
        self._dom = xml.dom.minidom.parseString(data)
        # Spine
        spine_list = self._dom.getElementsByTagName("spine")
        if len(spine_list) == 0:
            raise SpineMissing()
        elif len(spine_list) != 1:
            raise MoreThanOneSpine("{0} spines".format(len(spine_list)))
        self.spine = tuple(node.getAttribute("idref")
                for node in spine_list[0].getElementsByTagName("itemref"))
        # Manifest
        manifest_list = self._dom.getElementsByTagName("manifest")
        if len(manifest_list) == 0:
            raise ManifestMissing()
        elif len(manifest_list) != 1:
            raise MoreThanOneManifest("{0} manifests".format(len(manifest_list)))
        self.manifest = dict(
                (node.getAttribute("id"), node.getAttribute("href"))
                for node in manifest_list[0].getElementsByTagName("item"))

class Epub(object):
    def __init__(self, filename=None):
        self.filename = filename

    def zip_get_name(self, name_searched):
        for name in self._zipfile.namelist():
            # forward slash is always used in ZipFile pathnames
            filename = name.split("/")[-1]
            if filename == name_searched:
                return name
        return None

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename
        self.toc = self.content = self._zipfile = None
        if self._filename:
            self._zipfile = ZipFile(self._filename)
            self.toc = Toc(self._zipfile.read(self.toc_filename))
            self.content = Content(self._zipfile.read(self.content_filename))

    @property
    def zipfile(self):
        return self._zipfile

    @property
    def toc_filename(self):
        name = self.zip_get_name(TOC_NAME)
        if name:
            return name
        raise TocFileNotFound(name)

    @property
    def content_filename(self):
        name = self.zip_get_name(CONTENT_NAME)
        if name:
            return name
        raise ContentFileNotFound(name)

    def create_preview(self, filename, spine, missing_page=None, overwrite=False):
        """ Create a preview, writing filename, with only spine elements,
        with an optional missing_page for missing links and return an ePub """
        for item in spine:
            if not item in self.content.spine:
                raise ElementNotInSpine(item)
        # Check filename
        if os.path.exists(filename) and not overwrite:
            raise PreviewAlreadyExists(filename)
        # First loop
        for name in self._zipfile.filelist:
            data = self._zipfile.read(name)
            # href
            for match in re.finditer(r"<a (.* )?href=\"\", data):
                print match
                import pdb;pdb.set_trace()
            #print name, dir(name), len(data)
            #import pdb;pdb.set_trace()
            # TODO
            # harvest links
        #http://stackoverflow.com/questions/4890860/make-in-memory-copy-of-a-zip-by-iterrating-over-each-file-of-the-input
        zip_out = ZipFile(filename, mode='w')
        for name in self._zipfile.filelist:
            data = self._zipfile.read(name)
            # TODO
            # check in in spine
            zip_out.writestr(name, data)
        zip_out.close()
