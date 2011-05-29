# -*- coding: utf-8 -*-

import unittest
from epyub.epub import URLLister


class URLLIsterTest(unittest.TestCase):
    lister = URLLister("test/images/x.html")

    def testAbsolutize(self):
        self.assertEqual(self.lister.absolutize("abcd.xtml"), "test/images/abcd.xtml")
        self.assertEqual(self.lister.absolutize("../paperino.xtml"), "test/paperino.xtml")
        self.assertEqual(self.lister.absolutize("../paperino/../pluto.xtml"), "test/pluto.xtml")
        self.assertEqual(self.lister.absolutize("../paperino/./pluto.xtml"), "test/paperino/pluto.xtml")
        self.assertEqual(self.lister.absolutize("../../paperino/./pluto.xtml"), "paperino/pluto.xtml")
