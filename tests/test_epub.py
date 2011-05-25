# -*- coding: utf-8 -*-

import unittest
import os
from zipfile import ZipFile
from epyub.epub import Epub


class EpubTest(unittest.TestCase):
    epub_path = os.path.dirname(__file__)
    epub = os.path.join(epub_path, 'epub', 'andersen_40_novelle.epub')
    preview_epub = os.path.join(epub_path, 'epub', 'tmp_epub.epub')
    spine = ("Section0001.xhtml",
             "Section0002.xhtml",
             "Section0003.xhtml",
             "Section0004.xhtml",
             "Section0005.xhtml",
             "Section0006.xhtml",
             )

    def testEpubOpening(self):
        book = Epub(self.epub)
        self.assertTrue(isinstance(book.zipfile, ZipFile))

    def testEpubSpine(self):
        book = Epub(self.epub)
        self.assertEqual(book.content.spine, self.spine)

    def testEpubWrongPreview(self):
        from epyub.exceptions import ElementNotInSpine
        book = Epub(self.epub)
        self.assertRaises(ElementNotInSpine, book.create_preview, 'dummy', 'wrong')

    def testEpubPreview(self):
        book = Epub(self.epub)
        if os.path.exists(self.preview_epub):
            os.remove(self.preview_epub)
        new_book = book.create_preview(self.preview_epub, self.spine[0:2])
        #TODO check preview
        # Remove file
        #os.remove(self.preview_epub)
