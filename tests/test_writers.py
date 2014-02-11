#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Writer test.

File: test_writers.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""
import sys
from flexmock import flexmock
import unittest

from tcrawl.writers import FileWriter
from tcrawl.writers import JsonEncoder


class TestFileWriter(unittest.TestCase):

    def test_plain(self):
        mock_file = flexmock(write=lambda x: None,
                             flush=lambda: None,
                             close=lambda: None)
        flexmock(mock_file).should_receive('write').once().with_args('READY')
        flexmock(mock_file).should_receive('write').once().with_args('\n')
        flexmock(mock_file).should_receive('flush').once()
        flexmock(mock_file).should_receive('close').once()
        mock_open = flexmock(sys.modules['__builtin__'])
        mock_open.should_call('open')
        (mock_open.should_receive('open')
         .with_args('newfile', 'wb')
         .and_return(mock_file))
        wr = FileWriter('newfile')
        wr.write('READY')
        wr.close()

    def test_compressed(self):
        mock_file = flexmock(write=lambda x: None,
                             flush=lambda: None,
                             close=lambda: None)
        flexmock(mock_file).should_receive('write').once().with_args('READY')
        flexmock(mock_file).should_receive('write').once().with_args('\n')
        flexmock(mock_file).should_receive('flush').once()
        flexmock(mock_file).should_receive('close').once()
        mock_open = flexmock(sys.modules['gzip'])
        mock_open.should_call('open')
        (mock_open.should_receive('open')
         .with_args('newfile', 'wb')
         .and_return(mock_file))
        wr = FileWriter('newfile', compressed=True)
        wr.write('READY')
        wr.close()


class TestJsonEncoder(unittest.TestCase):

    """Test case docstring."""

    def test_write(self):
        mock_ostream = flexmock(write=lambda x: None,
                                close=lambda: None)
        (flexmock(mock_ostream).should_receive('write').once()
         .with_args('{"msg": "test"}'))
        flexmock(mock_ostream).should_receive('close').once()
        wr = JsonEncoder(mock_ostream)
        wr.write({'msg': 'test'})
        wr.close()
