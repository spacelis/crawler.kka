#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Testint actors.

File: test_actors.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""
import sys
from gevent import monkey
monkey.patch_all()
import unittest
from flexmock import flexmock

from pykka import ActorRegistry

from tcrawl.actors import Collector
from tcrawl.actors import TaskSource
from tcrawl.actors import Crawler
from tcrawl.writers import FileWriter
from tcrawl import Record

import logging
_logger = logging.getLogger(__name__)


class TestCollector(unittest.TestCase):  # pylint: disable=R0904

    """Test case docstring."""

    def setUp(self):
        self.controller = flexmock(tell=lambda x: None)

    def tearDown(self):
        pass

    def test_write(self):  # pylint: disable=R0201
        """ Test writing to a writable.  """
        mock_open = flexmock(sys.modules['__builtin__'])
        mock_open.should_call('open')
        (mock_open.should_receive('open')
         .with_args('newfile', 'wb')
         .and_return(
             flexmock(write=lambda x: None)
             .should_receive('write').with_args('READY').once().mock()
             .should_receive('flush').once().mock()
             .should_receive('close').once().mock()
             )
         )
        wr = FileWriter('newfile')
        c = Collector.start(self.controller, wr)
        c.tell(Record(None, 'READY'))
        ActorRegistry.stop_all()

    def test_fail(self):   # pylint: disable=R0201
        """ Test closing stream when fail. """
        def buggy_write(_):
            """ A buggy writable """
            raise ValueError()
        c = Collector.start(self.controller,
                            flexmock(write=buggy_write)
                            .should_receive('close').once().mock())

        c.tell(Record(None, 'Fail'))
        ActorRegistry.stop_all()


class TestTaskSource(unittest.TestCase):  # pylint: disable=R0904

    """Test case docstring."""

    def setUp(self):
        self.controller = flexmock(tell=lambda x: None)

    def tearDown(self):
        pass

    def test_request_task(self):
        """ test request task. """
        class MockWorker(object):
            """ MockWorker"""
            def work_on(self, w):
                _logger.debug('work on [%s]', w)
        (flexmock(MockWorker).should_call('__init__')
         .once().with_args(('INITARGS', )))
        (flexmock(MockWorker)
         .should_receive('work_on').once().with_args(0).ordered())
        (flexmock(MockWorker)
         .should_receive('work_on').once().with_args(1).ordered())
        (flexmock(MockWorker)
         .should_receive('work_on').once().with_args(2).ordered())

        (flexmock(Collector).should_receive('write').times(3))
        cl = Collector.start(self.controller,
                             flexmock(write=lambda x: None,
                                      close=lambda: None))
        ts = TaskSource.start(self.controller, range(3))
        cr = Crawler.start(self.controller, cl, ts, MockWorker, ('INITARGS', ))
        cr.actor_stopped.wait(3)
        ActorRegistry.stop_all()


if __name__ == '__main__':
    unittest.main()
