# -*- coding: utf-8 -*-

from zipfile import ZipFile

class Epub(object):
    def __init__(self, filename=None):
        self.filename = filename

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename
        if self._filename:
            self._zipfile = ZipFile(self._filename)
        else:
            self._zipfile = None

    @property
    def zipfile(self):
        return self._zipfile
