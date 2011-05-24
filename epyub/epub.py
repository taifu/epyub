# -*- coding: utf-8 -*-

from zipfile import ZipFile
from exceptions import *
import xml.dom.minidom

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
            raise MoreThanOneSpine()
        self.spine = tuple(node.getAttribute("idref")
                for node in spine_list[0].getElementsByTagName("itemref"))

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
        raise TocFileNotFound

    @property
    def content_filename(self):
        name = self.zip_get_name(CONTENT_NAME)
        if name:
            return name
        raise ContentFileNotFound

    def create_preview(self, filename, spine):
        for item in spine:
            if not item in self.content.spine:
                raise ElementNotInSpine(item)
        #TODO
