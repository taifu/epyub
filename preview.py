# -*- coding: utf-8 -*-

from epyub.epub import Epub


mahler = Epub("../epub/9788865760277.epub")
miyazaki = Epub("../epub/9788881249329.epub")
america = Epub("../epub/9788865060179.epub")

#for book in (mahler, miyazaki, america):
#    print book.zipfile.filename
#    print "\n".join("\t%d\t%s" % (i, spine) for i, spine in enumerate(mahler.content.spine))

mahler.create_preview("../epub/mahler_preview.epub", [
        "cover", "Frontespizio", "Colophon", "capitolo1", "capitolo9", "capitolo10", "Glossario"
        ], overwrite=True)
miyazaki.create_preview("../epub/miyazaki_preview.epub", [
        "cover", "postfazione", "colophon", "frontespizio", "Ringraziamenti", "prefazione", "epilogo", "capitolo_01", "bibliografia",
        ], overwrite=True)
america.create_preview("../epub/america_preview.epub", [
        "cover", "frontmatter1", "title", "copy", "frontmatter2", "frontmatter3", "frontmatter4", "frontmatter5", "image1", "image1a", "chapter1", "backmatter1", "backmatter2",
        ], overwrite=True)
