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
    metadata_content_urls = set(["OEBPS/toc.ncx", "OEBPS/Images/copertina.png"])
    manifest_keys = set([
            "ncx", "copertina.png", "e-text.png", "Style0001.css",
            "Section0001.xhtml", "Section0002.xhtml", "Section0003.xhtml",
            "Section0004.xhtml", "Section0005.xhtml", "Section0006.xhtml",
            ])
    urls_used_into_id = {
            "ncx": set([
                'OEBPS/Text/Section0001.xhtml', 'OEBPS/Text/Section0002.xhtml',
                'OEBPS/Text/Section0003.xhtml', 'OEBPS/Text/Section0004.xhtml',
                'OEBPS/Text/Section0005.xhtml', 'OEBPS/Text/Section0006.xhtml']),
            "Style0001.css": set([]),
            "copertina.png": set([]),
            "e-text.png": set([]),
            "Style0001.css": set([]),
            "Section0001.xhtml": set([
                'OEBPS/Styles/Style0001.css', 'OEBPS/Text/Section0002.xhtml',
                'OEBPS/Images/copertina.png']),
            "Section0002.xhtml": set([
                'OEBPS/Images/e-text.png', 'http://www.liberliber.it/sostieni/',
                'http://www.e-text.it/', 'http://www.liberliber.it/biblioteca/licenze/',
                'OEBPS/Styles/Style0001.css', 'http://www.liberliber.it/']),
            "Section0003.xhtml": set([
                'OEBPS/Styles/Style0001.css', 'OEBPS/Text/Section0006.xhtml']),
            "Section0004.xhtml": set([
                'OEBPS/Styles/Style0001.css', 'OEBPS/Text/Section0006.xhtml']),
            "Section0005.xhtml": set([
                'OEBPS/Styles/Style0001.css', 'OEBPS/Text/Section0006.xhtml']),
            "Section0006.xhtml": set([
                'OEBPS/Styles/Style0001.css', 'OEBPS/Text/Section0004.xhtml',
                'OEBPS/Text/Section0003.xhtml', 'OEBPS/Text/Section0005.xhtml']),
            }

    def testEpubOpening(self):
        book = Epub(self.epub)
        self.assertTrue(isinstance(book.zipfile, ZipFile))

    def testEpubContent(self):
        book = Epub(self.epub)
        self.assertEqual(book.content.spine, self.spine)
        self.assertEqual(set(book.content.manifest.keys()), self.manifest_keys)
        self.assertEqual(book.content.metadata_content_urls, self.metadata_content_urls)
        self.assertEqual(book.urls_used_into_id, self.urls_used_into_id)

    def testEpubWrongPreview(self):
        from epyub.exceptions import ElementNotInSpine
        book = Epub(self.epub)
        self.assertRaises(ElementNotInSpine, book.create_preview, 'dummy', 'wrong')

    def testEpubPreview(self):
        book = Epub(self.epub)
        if os.path.exists(self.preview_epub):
            os.remove(self.preview_epub)
        new_book = book.create_preview(self.preview_epub, self.spine[2:4])

        book = Epub(self.epub)
        book.create_preview("andersen_1.epub", book.content.spine[:3], overwrite=True)
        #book.create_preview("andersen_1.epub", self.spine[:3]

        book = Epub(self.epub)
        book.create_preview("andersen_2.epub", [self.spine[0], self.spine[2], self.spine[4], self.spine[5]], overwrite=True)

        #TODO check preview
        # Remove file
        #os.remove(self.preview_epub)
