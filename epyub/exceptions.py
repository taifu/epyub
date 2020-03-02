# -*- coding: utf-8 -*-

class ContainerFileNotFound(Exception):
    "The epub doesn't contain a container file"
    pass

class ContentFileNotFound(Exception):
    "The epub doesn't contain a content file"
    pass

class NcxFileNotFound(Exception):
    "The epub doesn't contain a ncx file"
    pass

class RootfilesMissing(Exception):
    "The container doesn't contain a rootfiles element"
    pass

class MoreThanOneRootfiles(Exception):
    "The container contains more than one rootfiles element"
    pass

class RootfileMissing(Exception):
    "The rootfiles node doesn't contain a OEBPS rootfile element"
    pass

class MetadataMissing(Exception):
    "The content doesn't contain a metadata element"
    pass

class SpineMissing(Exception):
    "The content doesn't contain a spine element"
    pass

class MoreThanOneSpine(Exception):
    "The content contains more than one spine element"
    pass

class ManifestMissing(Exception):
    "The content doesn't contain a manifest element"
    pass

class MoreThanOneManifest(Exception):
    "The content contains more than one manifest element"
    pass

class ElementNotInSpine(Exception):
    "The element doesn't exist in spine"
    pass

class PreviewAlreadyExists(Exception):
    "Preview filename already exists"
    pass

