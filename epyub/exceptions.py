# -*- coding: utf-8 -*-

class TocFileNotFound(Exception):
    "The epub doesn't contain a toc file"
    pass

class ContentFileNotFound(Exception):
    "The epub doesn't contain a content file"
    pass

class SpineMissing(Exception):
    "The container doesn't contain a spine element"
    pass

class MoreThanOneSpine(Exception):
    "The container contains more than one spine element"
    pass

class ElementNotInSpine(Exception):
    "The element doesn't exist in spine"
    pass

class PreviewAlreadyExists(Exception):
    "Preview filename already exists"
    pass

