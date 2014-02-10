#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Test the main module.

File: test_basic.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""
import sys
import unittest
from pykka import registry
from flexmock import flexmock
from tcrawl import Message
from tcrawl import Record
from tcrawl import TaskRequest
from tcrawl.actors import Collector
from tcrawl.writers import FileWriter

import logging
logging.getLogger('pykka').setLevel(logging.DEBUG)


class TestMessage(unittest.TestCase):  # pylint: disable=R0904

    """ Test the __init__.py """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_messages(self):
        """ Test automatci identifier. """
        Message._next_id = 0  # pylint: disable=W0212
        m1 = Message(None)
        m2 = Message(None)
        self.assertEqual(m1.identifier, 0)
        self.assertEqual(m2.identifier, 1)

    def test_match(self):
        """ test match """
        m1 = Record(None, {'msg': 'READY'})
        m2 = TaskRequest(None)
        m3 = Message(None)
        m1.match({
            Record.N(): lambda msg: None,
            TaskRequest.N(): lambda msg: self.fail(),
            '_': lambda msg: self.fail(),
        })
        m2.match({
            Record.N(): lambda msg: self.fail(),
            TaskRequest.N(): lambda msg: None,
            '_': lambda msg: self.fail(),
        })
        m3.match({
            Record.N(): lambda msg: self.fail,
            TaskRequest.N(): lambda msg: self.fail(),
            '_': lambda msg: None,
        })

        def err_match():
            """ raise a non-matched"""
            m3.match({})
        self.assertRaises(ValueError, err_match)


class TestLog(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_logging(self):
        """ Test logging """
        import gevent
        import logging
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        def dummylogging(source):
            """ dummy """
            logger.debug("test_logging from" + source)

        dummylogging('main')
        g = gevent.spawn(dummylogging('greenlet'))
        g.join(1)
        #raise ValueError()


if __name__ == '__main__':
    unittest.main()
