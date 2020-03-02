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
    html_toc = u"""<ul class="toc">
  <li>Copertina</li>
  <li>Informazioni</li>
  <li>GIOSUE CARDUCCI ALLA TRADUTTRICE</li>
  <li>H. C. ANDERSEN</li>
  <ul>
    <li>I.</li>
    <ul>
      <li>TESTA - DI - PIPA E TESTA SODA</li>
    </ul>
    <li>II.</li>
  </ul>
  <li>FONTI</li>
  <li>NOVELLE</li>
  <ul>
    <li>IL BRUTTO ANITROCCOLO</li>
    <li>I VESTITI NUOVI DELL'IMPERATORE</li>
    <li>STORIA DI UNA MAMMA</li>
    <li>L'ACCIARINO</li>
    <li>LA MARGHERITINA</li>
    <li>LA CHIOCCIOLA E IL ROSAIO</li>
    <li>L'INTREPIDO SOLDATINO DI STAGNO</li>
    <li>LA SIRENETTA</li>
    <li>LA PICCINA DEI FIAMMIFERI</li>
    <li>L'ABETE</li>
    <li>L'AGO</li>
    <li>L'USIGNUOLO</li>
    <li>I PROMESSI SPOSI</li>
    <li>CECCHINO E CECCONE</li>
    <li>POLLICINA</li>
    <li>GALLETTO MASSARO E GALLETTO BANDERUOLA</li>
    <li>LA PRINCIPESSINA SUL PISELLO</li>
    <li>IL GUARDIANO DI PORCI</li>
    <li>IL RAGAZZACCIO</li>
    <li>QUEL CHE FA IL BABBO È SEMPRE BEN FATTO</li>
    <li>IL MONTE DEGLI ELFI</li>
    <li>L'ANGELO</li>
    <li>LE CORSE</li>
    <li>LA NONNA</li>
    <li>PENNA E CALAMAIO</li>
    <li>L'ULTIMA PERLA</li>
    <li>NEI MARI ESTREMI</li>
    <li>LA GARA DI SALTO</li>
    <li>IL LINO</li>
    <li>LA VECCHIA CASA</li>
    <li>CINQUE IN UN BACCELLO</li>
    <li>IL FOLLETTO SERRALOCCHI</li>
    <li>IL GORGO DELLA CAMPANA</li>
    <li>C'È DIFFERENZA</li>
    <li>L'OMBRA</li>
    <li>IL PICCOLO TUK</li>
    <li>«VERO VERISSIMO!»</li>
    <li>LA DILIGENZA DA DODICI POSTI</li>
    <li>IL VECCHIO FANALE</li>
    <li>IL ROSPO</li>
  </ul>
  <li>Note</li>
</ul>
"""
    html_href_toc = u"""<ul class="toc">
  <li><a href="Text/Section0001.xhtml">Copertina</a></li>
  <li><a href="Text/Section0002.xhtml">Informazioni</a></li>
  <li><a href="Text/Section0003.xhtml">GIOSUE CARDUCCI ALLA TRADUTTRICE</a></li>
  <li><a href="Text/Section0003.xhtml#heading_id_3">H. C. ANDERSEN</a></li>
  <ul>
    <li><a href="Text/Section0003.xhtml#heading_id_4">I.</a></li>
    <ul>
      <li><a href="Text/Section0003.xhtml#heading_id_5">TESTA - DI - PIPA E TESTA SODA</a></li>
    </ul>
    <li><a href="Text/Section0003.xhtml#heading_id_6">II.</a></li>
  </ul>
  <li><a href="Text/Section0003.xhtml#heading_id_7">FONTI</a></li>
  <li><a href="Text/Section0004.xhtml">NOVELLE</a></li>
  <ul>
    <li><a href="Text/Section0004.xhtml#heading_id_9">IL BRUTTO ANITROCCOLO</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_10">I VESTITI NUOVI DELL'IMPERATORE</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_11">STORIA DI UNA MAMMA</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_12">L'ACCIARINO</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_13">LA MARGHERITINA</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_14">LA CHIOCCIOLA E IL ROSAIO</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_15">L'INTREPIDO SOLDATINO DI STAGNO</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_16">LA SIRENETTA</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_17">LA PICCINA DEI FIAMMIFERI</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_18">L'ABETE</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_19">L'AGO</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_20">L'USIGNUOLO</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_21">I PROMESSI SPOSI</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_22">CECCHINO E CECCONE</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_23">POLLICINA</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_24">GALLETTO MASSARO E GALLETTO BANDERUOLA</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_25">LA PRINCIPESSINA SUL PISELLO</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_26">IL GUARDIANO DI PORCI</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_27">IL RAGAZZACCIO</a></li>
    <li><a href="Text/Section0004.xhtml#heading_id_28">QUEL CHE FA IL BABBO È SEMPRE BEN FATTO</a></li>
    <li><a href="Text/Section0005.xhtml">IL MONTE DEGLI ELFI</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_30">L'ANGELO</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_31">LE CORSE</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_32">LA NONNA</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_33">PENNA E CALAMAIO</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_34">L'ULTIMA PERLA</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_35">NEI MARI ESTREMI</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_36">LA GARA DI SALTO</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_37">IL LINO</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_38">LA VECCHIA CASA</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_39">CINQUE IN UN BACCELLO</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_40">IL FOLLETTO SERRALOCCHI</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_41">IL GORGO DELLA CAMPANA</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_42">C'È DIFFERENZA</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_43">L'OMBRA</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_44">IL PICCOLO TUK</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_45">«VERO VERISSIMO!»</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_46">LA DILIGENZA DA DODICI POSTI</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_47">IL VECCHIO FANALE</a></li>
    <li><a href="Text/Section0005.xhtml#heading_id_48">IL ROSPO</a></li>
  </ul>
  <li><a href="Text/Section0006.xhtml">Note</a></li>
</ul>
"""
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
        preview_spine = self.spine[2:4]
        book.create_preview(self.preview_epub, preview_spine)
        preview_book = Epub(self.preview_epub)
        self.assertEqual(tuple(name.filename for name in preview_book.zipfile.infolist()),
                ('mimetype', 'META-INF/container.xml', 'OEBPS/content.opf', 'OEBPS/toc.ncx',
                 'OEBPS/Images/copertina.png', 'OEBPS/Styles/Style0001.css',
                 'OEBPS/Text/Section0003.xhtml', 'OEBPS/Text/Section0004.xhtml',))
        self.assertEqual(preview_book.content.spine, preview_spine)
        self.assertEqual(set(preview_book.content.manifest.keys()), set([
            u'ncx', u'Section0004.xhtml', u'Section0003.xhtml', u'Style0001.css', u'copertina.png']))
        self.assertEqual(preview_book.content.metadata_content_urls, set([
            u'OEBPS/toc.ncx', u'OEBPS/Images/copertina.png']))
        self.assertEqual(preview_book.urls_used_into_id, {
            u'ncx': set(['OEBPS/Text/Section0004.xhtml', 'OEBPS/Text/Section0003.xhtml']),
            u'Section0004.xhtml': set(['OEBPS/Styles/Style0001.css']),
            u'Section0003.xhtml': set(['OEBPS/Styles/Style0001.css']),
            u'Style0001.css': set([]), u'copertina.png': set([])})
        del preview_book
        os.remove(self.preview_epub)

    def testEpubEtichette(self):
        book = Epub(self.epub)
        self.assertEqual(book.ncx.html_toc, self.html_toc)

    def testEpubTocHtml(self):
        book = Epub(self.epub)
        self.assertEqual(book.ncx.html_href_toc, self.html_href_toc)
