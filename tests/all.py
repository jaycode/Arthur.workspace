"""
This module contains all the modules containing doctest.
Don't forget to include more modules as more doctests are added.
"""

import os, sys, inspect
# This needs to be included here to ensure path is loaded from app main directory.
base_path = os.path.realpath(
    os.path.abspath(
        os.path.join(
            os.path.split(
                inspect.getfile(
                    inspect.currentframe()
                )
            )[0],
            '..'
        )
    )
)
sys.path.append(base_path)

import unittest
import doctest 
import lib.filesystem.base
import app.mod_cmd.commands.docs.list_docs as list_docs

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(lib.filesystem.base))
    tests.addTests(doctest.DocTestSuite(list_docs))
    return tests

if __name__ == '__main__':
    unittest.main()