# -*- coding: utf-8 -*-

import os.path
from urlparse import urlparse
from zipfile import ZipFile
import xml.dom.minidom
from sgmllib import SGMLParser
from collections import deque
import epyub.exceptions as epexc

# Mandatory paths
OEBPS_PATH = "OEBPS"
CONTAINER_NAME = "META-INF/container.xml"
MIMETYPE_NAME = "mimetype"

# Media type
MEDIA_TYPE_OEBPS = "application/oebps-package+xml"
MEDIA_TYPE_NCX = "application/x-dtbncx+xml"
MEDIA_TYPE_XHTML = "application/xhtml+xml"
MEDIA_TYPE_DTBOOK = "application/x-dtbook+xml"

class Item(object):
    def __init__(self, id, url, media_type):
        self.id = id
        self.url = url
        self.media_type = media_type

    def parsable(self):
        if self.media_type.endswith("xml"):
            return True
        return False

class Container(object):
    """ Mandatory META-INF/container.xml file """
    def __init__(self, data):
        self._dom = xml.dom.minidom.parseString(data)
        # Root file
        rootfiles = self._dom.getElementsByTagName("rootfiles")
        if len(rootfiles) == 0:
            raise epexc.RootfilesMissing()
        elif len(rootfiles) != 1:
            raise epexc.MoreThanOneRootfiles("{0} rootfiles".format(len(rootfiles)))
        for node in rootfiles[0].getElementsByTagName("rootfile"):
            if node.getAttribute("media-type") == MEDIA_TYPE_OEBPS:
                self.rootfile = node.getAttribute("full-path")
                break
        else:
            raise epexc.RootfileMissing()

class Content(object):
    """ Content file ( usually OEBPS/content.opf ) """
    def __init__(self, data):
        self._dom = xml.dom.minidom.parseString(data)
        # Manifest (and urls)
        manifests = self._dom.getElementsByTagName("manifest")
        if len(manifests) == 0:
            raise epexc.ManifestMissing()
        elif len(manifests) != 1:
            raise epexc.MoreThanOneManifest("{0} manifests".format(len(manifests)))
        self.manifest = {}
        self.urls_by_id = {}
        self.ncx_item = None
        for node in manifests[0].getElementsByTagName("item"):
            id = node.getAttribute("id")
            url = OEBPS_PATH + "/" + node.getAttribute("href")
            media_type = node.getAttribute("media-type")
            self.manifest[id] = Item(id, url, media_type)
            self.urls_by_id[url] = id
            if media_type == MEDIA_TYPE_NCX:
                self.ncx_item = self.manifest[id]
        # Spine
        spines = self._dom.getElementsByTagName("spine")
        if len(spines) == 0:
            raise epexc.SpineMissing()
        elif len(spines) != 1:
            raise epexc.MoreThanOneSpine("{0} spines".format(len(spines)))
        self.spine = tuple(node.getAttribute("idref")
                for node in spines[0].getElementsByTagName("itemref"))
        # Metadata
        self.metadata_content_urls = set([self.ncx_item.url])
        try:
            metadata = self._dom.getElementsByTagName("metadata")[0]
            for node in metadata.childNodes:
                # Content used in metadata
                if node.nodeType == node.ELEMENT_NODE and node.getAttribute("name") == "cover":
                    id = node.getAttribute("content")
                    if id:
                        self.metadata_content_urls.add(self.manifest[id].url)
        except IndexError:
            raise epexc.MetadataMissing()

class Ncx(object):
    """ Table of content file ( usually OEBPS/toc.ncx ) """
    def __init__(self, data):
        self._dom = xml.dom.minidom.parseString(data)

class URLLister(SGMLParser):
    def __init__(self, parent_path, *args, **kwargs):
        self.parent_path_parts = parent_path.split("/")[:-1]
        #SGMLParser is an old style classe
        SGMLParser.__init__(self, *args, **kwargs)

    """ Used to harvers URL from files """
    def reset(self):
        SGMLParser.reset(self)
        self.urls = set()

    def absolutize(self, url):
        p = urlparse(url)
        # Not an absolute path
        if not p.scheme:
            parts = self.parent_path_parts[:] + p.path.split("/") # Get a copy!
            while "." in parts:
                parts.pop(parts.index("."))
            while ".." in parts[1:]:
                i = parts.index("..")
                parts[i-1:i+1] = []
            return "/".join(parts)
        return url

    def harvest(self, attrs, attribute):
        attributes = [v for k, v in attrs if k==attribute]
        if len(attributes) > 0:
            url = self.absolutize(attributes[0])
            self.urls.add(url)

    def start_content(self, attrs):
        self.harvest(attrs, 'src')

    def start_link(self, attrs):
        self.harvest(attrs, 'href')

    def start_img(self, attrs):
        self.harvest(attrs, 'src')

    def start_a(self, attrs):
        self.harvest(attrs, 'href')

class Epub(object):
    def __init__(self, filename=None):
        self.filename = filename

    def zip_get_name(self, name_searched):
        for name in self._zipfile.namelist():
            if name == name_searched:
                return name
        return None

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename
        self.ncx = self.content = self._zipfile = None
        if self._filename:
            self._zipfile = ZipFile(self._filename)
            self.container = Container(self._zipfile.read(CONTAINER_NAME))
            self.content = Content(self._zipfile.read(self.content_filename))
            self.ncx = Ncx(self._zipfile.read(self.content.ncx_item.url))
            # Harvest URLs from parsable files
            self.urls_used_into_id = {}
            for name in self._zipfile.infolist():
                data = self._zipfile.read(name)
                url = str(name.filename)
                if url in self.content.urls_by_id:
                    item = self.content.manifest[self.content.urls_by_id[url]]
                    if item:
                        urls = set()
                        if item.parsable():
                            parser = URLLister(parent_path=url)
                            parser.feed(data)
                            for url_found in parser.urls:
                                urls.add(url_found)
                        self.urls_used_into_id[item.id] = urls

    @property
    def zipfile(self):
        return self._zipfile

    @property
    def container_filename(self):
        name = self.zip_get_name(CONTAINER_NAME)
        if name:
            return name
        raise epexc.ContainerFileNotFound(name)

    @property
    def content_filename(self):
        name = self.zip_get_name(self.container.rootfile)
        if name:
            return name
        raise epexc.ContentFileNotFound(name)

    def create_preview(self, preview_filename, spine_preview, missing_page=None, overwrite=False):
        """ Create a preview, writing filename, with only spine elements,
        with an optional missing_page for missing links and return an ePub """
        for item in spine_preview:
            if not item in self.content.spine:
                raise epexc.ElementNotInSpine(item)
        # Check preview_filename
        if os.path.exists(preview_filename) and not overwrite:
            raise epexc.PreviewAlreadyExists(preview_filename)

        # Spine IDs and URLs removed from preview
        spine_ids_removed = set(id for id in self.content.spine if id not in spine_preview)
        urls_to_be_removed = set(self.content.manifest[id].url for id in spine_ids_removed)

        # Recursively check URLs used (content urls are always included)
        used_urls = set(self.content.metadata_content_urls)
        exploring_ids = deque(spine_preview)
        explored_ids = set()
        while exploring_ids:
            id = exploring_ids.popleft()
            # Explored id only if is internal, not explored and not removed
            if id in self.content.manifest and not id in explored_ids and not id in spine_ids_removed:
                used_urls.add(self.content.manifest[id].url)
                for url in self.urls_used_into_id[id]:
                    if url in self.content.urls_by_id and not url in urls_to_be_removed:
                        used_urls.add(url)
                        exploring_ids.append(self.content.urls_by_id[url])
            explored_ids.add(id)

        # Check every url in manifest if not used
        for id, item in self.content.manifest.items():
            if not item.url in used_urls:
                urls_to_be_removed.add(item.url)

        #http://stackoverflow.com/questions/4890860/make-in-memory-copy-of-a-zip-by-iterrating-over-each-file-of-the-input

        zip_out = ZipFile(preview_filename, mode='w')
        for name in self._zipfile.infolist():
            url = name.filename
            if not url in urls_to_be_removed:
                data = self._zipfile.read(name)
                if url in self.content.manifest:
                    item = self.content.manifest[self.content.urls_by_id[url]]
                    if item.parsable():
                        pass
                zip_out.writestr(name, data)
        zip_out.close()
