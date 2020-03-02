# -*- coding: utf-8 -*-

import sys
import os
import glob
import unittest

def main(verbosity):
    _parts = os.path.abspath(__file__).split(os.path.sep)
    parent_path = os.path.sep.join(_parts[:-2])
    cur_path = os.path.sep.join(_parts[:-1])
    sys.path.insert(0, parent_path)

    testloader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for test in glob.glob(os.path.join(cur_path, "test_*.py")):
        _filename = os.path.splitext(os.path.split(test)[1])[0]
        _module = __import__(_filename, globals(), locals(), ['*'], -1)
        suite.addTest(testloader.loadTestsFromModule(_module))

    unittest.TextTestRunner(verbosity=verbosity).run(suite)

if __name__ == "__main__":
    description = 'Run epyub test suite'
    verbosity_args = ('-v', '--verbosity')
    verbosity_kwargs = {'dest': 'verbosity', 'type':int,
            'help': 'verbosity', 'default': '1'}
    try:
        import argparse
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(*verbosity_args, **verbosity_kwargs)
        options = parser.parse_args()
    except ImportError:
        import optparse
        parser = optparse.OptionParser(description=description)
        parser.add_option(*verbosity_args, **verbosity_kwargs)
        (options, args) = parser.parse_args()

    main(verbosity=options.verbosity)
