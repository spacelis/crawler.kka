#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" test_readers.

File: test_readers.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
"""
import sys
from tcrawl.readers import CSVReader
from StringIO import StringIO
from textwrap import dedent

import unittest
from flexmock import flexmock


class TestReaders(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_csvreader(self):
        """ test csv reader """
        mock_file = flexmock(StringIO(
            dedent(
                """\
                id,name
                1,spaceli
                2,jojo
                """
            )))
        mock_file.should_call('close').once()

        mock_open = flexmock(sys.modules['__builtin__'])
        (mock_open.should_receive('open')
         .and_return(mock_file))
        r = flexmock(CSVReader('test'))

        r.should_call('__iter__')
        expected = [{'id': '1', 'name': 'spaceli'},
                    {'id': '2', 'name': 'jojo'}]
        for a, b in zip(r, expected):
            self.assertDictEqual(a, b)
        r.close()
