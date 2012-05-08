# -*- coding: utf-8 -*-

import os.path
import copy
import types
from urlparse import urlparse
from zipfile import ZipFile
import xml.dom.minidom
from HTMLParser import HTMLParser
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
    def __init__(self, data, file_url='OEBPS/content.opf'):
        self._dom = xml.dom.minidom.parseString(data)
        # Manifest (and urls)
        manifests = self._dom.getElementsByTagNameNS("*", "manifest")
        if len(manifests) == 0:
            raise epexc.ManifestMissing()
        elif len(manifests) != 1:
            raise epexc.MoreThanOneManifest("{0} manifests".format(len(manifests)))
        self.manifest = {}
        self.urls_by_id = {}
        self.ncx_item = None
        parent_path_parts = file_url.split("/")[:-1]
        for node in manifests[0].getElementsByTagNameNS("*", "item"):
            id = node.getAttribute("id")
            url = absolutize_url(node.getAttribute("href"), parent_path_parts)
            media_type = node.getAttribute("media-type")
            self.manifest[id] = Item(id, url, media_type)
            self.urls_by_id[url] = id
            if media_type == MEDIA_TYPE_NCX:
                self.ncx_item = self.manifest[id]
        # Spine
        spines = self._dom.getElementsByTagNameNS("*", "spine")
        if len(spines) == 0:
            raise epexc.SpineMissing()
        elif len(spines) != 1:
            raise epexc.MoreThanOneSpine("{0} spines".format(len(spines)))
        self.spine = tuple(node.getAttribute("idref")
                for node in spines[0].getElementsByTagNameNS("*", "itemref"))
        # Metadata
        self.cover_url = None
        self.metadata_content_urls = set([self.ncx_item.url])
        try:
            metadata = self._dom.getElementsByTagNameNS("*", "metadata")[0]
            for node in metadata.childNodes:
                # Content used in metadata
                if node.nodeType == node.ELEMENT_NODE and node.getAttribute("name") == "cover":
                    id = node.getAttribute("content")
                    if id:
                        if not id in self.manifest:
                            raise epexc.BadManifestIdentifier(id)
                        self.cover_url = self.manifest[id].url
                        self.metadata_content_urls.add(self.cover_url)
        except IndexError:
            raise epexc.MetadataMissing()

class Ncx(object):
    """ Table of content file ( usually OEBPS/toc.ncx ) """
    def __init__(self, data):
        self._dom = xml.dom.minidom.parseString(data)
        # Get hierarchical toc in a list of element and/or list etc.
        def get_text(navPoint):
            return navPoint.getElementsByTagNameNS("*", "navLabel")[0
                    ].getElementsByTagNameNS("*", "text")[0
                    ].childNodes[0].wholeText
        def get_navpoints(father):
            return [element for element in father.childNodes
                    if element.nodeType==element.ELEMENT_NODE and element.tagName=="navPoint"]
        toc_nodes = get_navpoints(self._dom.getElementsByTagNameNS("*", "navMap")[0])
        self._toc = [get_text(navpoint) for navpoint in toc_nodes]
        labels = deque([(toc_nodes, self._toc)])
        while labels:
            current_label, current_toc = labels.popleft()
            delta = 0
            for i, node in enumerate(current_label):
                sons = get_navpoints(node)
                if sons:
                    current_label[i] = sons
                    current_toc.insert(i + delta + 1, [get_text(navpoint) for navpoint in sons])
                    labels.append((current_label[i], current_toc[i + delta + 1]))
                    delta += 1

    @property
    def toc(self):
        return self._toc

    @property
    def html_toc(self):
        def explore(labels, level=0):
            indent = level * u"  "
            html = indent + u"<ul{0}>\n".format(u"" if level > 0 else u" class=\"toc\"")
            for label in labels:
                if type(label) == types.ListType:
                    html += explore(label, level+1)
                else:
                    html += u"{0}<li>{1}</li>\n".format(indent + u"  ", label)
            html += indent + u"</ul>\n"
            return html
        return explore(self.toc)

def absolutize_url(url, parent_path_parts):
    p = urlparse(url)
    # Not an absolute path
    if not p.scheme:
        parts = parent_path_parts[:] + p.path.split("/") # Get a copy!
        while "." in parts:
            parts.pop(parts.index("."))
        while ".." in parts[1:]:
            i = parts.index("..")
            parts[i-1:i+1] = []
        return "/".join(parts)
    return url

class URLLister(HTMLParser):
    def __init__(self, parent_path, *args, **kwargs):
        self.parent_path_parts = parent_path.split("/")[:-1]
        #SGMLParser is an old style classe
        HTMLParser.__init__(self, *args, **kwargs)

    def reset(self):
        HTMLParser.reset(self)
        self.urls = set()

    def absolutize(self, url):
        return absolutize_url(url, self.parent_path_parts)

    def harvest(self, attrs, attribute):
        attributes = [v for k, v in attrs if k==attribute]
        if len(attributes) > 0:
            url = self.absolutize(attributes[0])
            self.urls.add(url)

    def handle_starttag(self, tag, attrs):
        if tag in ("content", "img"):
            self.harvest(attrs, 'src')
        elif tag in ("link", "a"):
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
            self.content = Content(self._zipfile.read(self.content_filename), file_url=self.content_filename)
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

        # Write preview epub
        zip_out = ZipFile(preview_filename, mode='w')
        for name in self._zipfile.infolist():
            url = name.filename
            parent_path_parts = url.split("/")[:-1]
            insert_file = False
            if (not url in urls_to_be_removed):
                if url in (self.content_filename, CONTAINER_NAME, MIMETYPE_NAME):
                    insert_file = True
                elif url in self.content.urls_by_id:
                    insert_file = True
            if insert_file:
                data = self._zipfile.read(name)
                if url == self.content_filename:
                    dom = xml.dom.minidom.parseString(data)
                    # Process content manifest
                    for item in dom.getElementsByTagNameNS("*", "manifest")[0].getElementsByTagNameNS("*", "item"):
                        url = absolutize_url(item.getAttribute("href"), parent_path_parts)
                        if url in urls_to_be_removed:
                            try:
                                item.parentNode.removeChild(item)
                            except xml.dom.NotFoundErr:
                                pass
                    # Process content spine
                    for itemref in dom.getElementsByTagNameNS("*", "spine")[0].getElementsByTagNameNS("*", "itemref"):
                        url = self.content.manifest[itemref.getAttribute("idref")].url
                        if url in urls_to_be_removed:
                            try:
                                itemref.parentNode.removeChild(itemref)
                            except xml.dom.NotFoundErr:
                                pass
                    data = dom.toxml(dom.encoding)
                elif url in self.content.urls_by_id:
                    item = self.content.manifest[self.content.urls_by_id[url]]
                    if item == self.content.ncx_item:
                        # Process toc
                        dom = xml.dom.minidom.parseString(data)
                        for navPoint in dom.getElementsByTagNameNS("*", "navPoint"):
                            for node in navPoint.childNodes:
                                if node.nodeType == node.ELEMENT_NODE and node.nodeName == "content":
                                    url = absolutize_url(node.getAttribute("src"), parent_path_parts)
                                    if url in urls_to_be_removed:
                                        try:
                                            navPoint.parentNode.removeChild(navPoint)
                                        except xml.dom.NotFoundErr:
                                            pass
                        for cont, navPoint in enumerate(dom.getElementsByTagNameNS("*", "navPoint")):
                            playOrder = navPoint.getAttribute("playOrder")
                            if playOrder != str(cont + 1):
                                playOrder = navPoint.setAttribute("playOrder", str(cont + 1))
                        data = dom.toxml(dom.encoding)
                    elif item.parsable():
                        # Process generic html/xml
                        dom = xml.dom.minidom.parseString(data)
                        parent_path_parts = url.split("/")[:-1]
                        for tagname, attr in (("content", "src"), ("img", "src"), ("link", "href"), ("a", "href")):
                            for node in dom.getElementsByTagNameNS("*", tagname):
                                if node.nodeType == node.ELEMENT_NODE:
                                    url = absolutize_url(node.getAttribute(attr), parent_path_parts)
                                    if url in urls_to_be_removed:
                                        try:
                                            node.parentNode.removeChild(node)
                                        except xml.dom.NotFoundErr:
                                            pass
                        data = dom.toxml(dom.encoding)
                zip_out.writestr(copy.deepcopy(name), data)
        zip_out.close()
