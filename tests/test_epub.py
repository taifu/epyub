# -*- coding: utf-8 -*-

import unittest
import os
from zipfile import ZipFile
from epyub.epub import Epub

class EpubTest(unittest.TestCase):
    epub_path = os.path.dirname(__file__)
    book1 = os.path.join(epub_path, 'epub', 'andersen_40_novelle.epub')

    def testEpubOpening(self):
        book = Epub(self.book1)
        book.filename = self.book1
        self.assertIsInstance(book.zipfile, ZipFile)
