# -*- coding: utf-8 -*-

import os.path
import re
from zipfile import ZipFile
import xml.dom.minidom
from sgmllib import SGMLParser
from epyub.exceptions import *

CONTENT_PATH = "OEBPS"
TOC_NAME = "toc.ncx"
CONTENT_NAME = "content.opf"
CONTAINER_NAME = "container.xml"
MIMETYPE_NAME = "mimetype"

class Toc(object):
    def __init__(self, data):
        self._dom = xml.dom.minidom.parseString(data)

class Item(object):
    def __init__(self, id, href, media_type):
        self.id = id
        self.href = href
        self.media_type = media_type

    def parsable(self):
        if 'html' in self.media_type or 'xml' in self.media_type:
            return True
        return False

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
        # Manifest and hrefs
        manifest_list = self._dom.getElementsByTagName("manifest")
        if len(manifest_list) == 0:
            raise ManifestMissing()
        elif len(manifest_list) != 1:
            raise MoreThanOneManifest("{0} manifests".format(len(manifest_list)))
        self.manifest = {}
        self.hrefs = {}
        for node in manifest_list[0].getElementsByTagName("item"):
            id = node.getAttribute("id")
            href = node.getAttribute("href")
            media_type = node.getAttribute("media-type")
            self.manifest[id] = Item(id, href, media_type)
            self.hrefs[href] = self.manifest[id]

class URLLister(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.links = set()

    def check(self, attrs, key):
        alls = [v for k, v in attrs if k==key]
        if alls:
            link = alls[0]
            if link.startswith("../"):
                link = link[3:]
            if not ":" in link[:7]: # mailto:
                if "#" in link:
                    link = link[:link.rfind("#")]
                self.links.add(link)

    def start_content(self, attrs):
        self.check(attrs, 'src')

    def start_link(self, attrs):
        self.check(attrs, 'href')

    def start_img(self, attrs):
        self.check(attrs, 'src')

    def start_a(self, attrs):
        self.check(attrs, 'href')

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
            # Harvest URLs from parsable files
            self.urls = {}
            for name in self._zipfile.infolist():
                data = self._zipfile.read(name)
                filename = str(name.filename)
                if filename.startswith(CONTENT_PATH):
                    filename = filename[len(CONTENT_PATH)+1:]
                if filename in self.content.hrefs:
                    item = self.content.hrefs.get(filename, None)
                    if item:
                        urls = set()
                        if item.parsable():
                            parser = URLLister()
                            parser.feed(data)
                            for url in parser.links:
                                urls.add(url)
                        self.urls[item.id] = urls
            print filename
            for k, v in self.urls.items():
                print k, v

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

    def create_preview(self, preview_filename, spine, missing_page=None, overwrite=False):
        """ Create a preview, writing filename, with only spine elements,
        with an optional missing_page for missing links and return an ePub """
        for item in spine:
            if not item in self.content.spine:
                raise ElementNotInSpine(item)
        # Check preview_filename
        if os.path.exists(preview_filename) and not overwrite:
            raise PreviewAlreadyExists(preview_filename)
        # First loop
        #for name in self._zipfile.filelist:


            # href
            #for match in re.finditer(r"<a (.* )?href=\"\", data):
            #    print match
            #    import pdb;pdb.set_trace()
            #print name, dir(name), len(data)
            #import pdb;pdb.set_trace()
            # TODO
            # harvest links
        #http://stackoverflow.com/questions/4890860/make-in-memory-copy-of-a-zip-by-iterrating-over-each-file-of-the-input
        zip_out = ZipFile(preview_filename, mode='w')
        for name in self._zipfile.infolist():
            data = self._zipfile.read(name)
            # TODO
            # check in in spine
            zip_out.writestr(name, data)
        zip_out.close()
