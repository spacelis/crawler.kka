#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Testint actors.

File: test_actors.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""
# pylint: disable=R0201,R0903,R0904,C0111
import gevent
from gevent import monkey
monkey.patch_all()

import sys
import unittest
from flexmock import flexmock

from pykka import ActorRegistry

from tcrawl.actors import Controller
from tcrawl.actors import Collector
from tcrawl.actors import TaskSource
from tcrawl.actors import Crawler
from tcrawl.writers import FileWriter
from tcrawl import Record
from tcrawl import Task
from tcrawl import NoMoreTask
from tcrawl import TaskRequest
from tcrawl import NonFatalFailure
from tcrawl import FatalFailure
from tcrawl import RecoverableError
from tcrawl import IgnorableError

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

    def test_return_task(self):
        """ test return task. """
        ctl = flexmock(actor_ref=flexmock(tell=lambda x: None))
        cr_ref = flexmock(tell=lambda x: None, kinds='cr')
        cr = flexmock(actor_ref=cr_ref)
        cr_ref.should_receive('tell').with_args(Task).at_least().times(3)
        cr_ref.should_receive('tell').with_args(NoMoreTask).once()
        ts = TaskSource.start(ctl, range(3))
        ts.tell(TaskRequest(cr))
        ts.tell(TaskRequest(cr))
        ts.tell(TaskRequest(cr))
        ts.tell(TaskRequest(cr))
        ts.stop()


class TestCrawler(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        self.controller = flexmock(tell=lambda x: None)
        self.tasksource = flexmock(tell=lambda x: None)
        self.collector = flexmock(tell=lambda x: None)
        self.initargs = (1, 2, 3)

    def tearDown(self):
        pass

    def test_work(self):
        class Worker(object):
            def __init__(self, arg):
                self.arg = arg

            def work_on(self, task):
                print task
                return task

        flexmock(Worker).should_call('work_on').once().with_args(1)
        cr = Crawler.start(self.controller, self.tasksource, self.collector,
                           Worker, self.initargs)
        cr.tell(Task(None, 1))
        cr.stop()
        ActorRegistry.stop_all()

    def test_failwork(self):
        class Worker(object):
            def __init__(self, arg):
                self.arg = arg

            def work_on(self, task):
                pass

        ctl = (flexmock(tell=lambda x: None)
               .should_receive('tell').once()
               .with_args(NonFatalFailure).mock())

        (flexmock(Worker, work_on=lambda x: None)
         .should_receive('work_on').once()
         .with_args(1).and_raise(RecoverableError(ValueError())))

        cr = Crawler.start(ctl, self.tasksource, self.collector,
                           Worker, self.initargs)
        cr.tell(Task(None, 1))
        cr.stop()
        ActorRegistry.stop_all()

    def test_failwork2(self):
        class Worker(object):
            def __init__(self, arg):
                self.arg = arg

            def work_on(self, task):
                pass

        ctl = (flexmock(tell=lambda x: None)
               .should_receive('tell').once()
               .with_args(NonFatalFailure).mock())

        (flexmock(Worker, work_on=lambda x: None)
         .should_receive('work_on').once()
         .with_args(1).and_raise(IgnorableError(ValueError())))

        cr = Crawler.start(ctl, self.tasksource, self.collector,
                           Worker, self.initargs)
        cr.tell(Task(None, 1))
        cr.stop()
        ActorRegistry.stop_all()

    def test_fatalfailwork(self):
        class Worker(object):
            def __init__(self, arg):
                self.arg = arg

            def work_on(self, task):
                pass

        ctl = (flexmock(tell=lambda x: None)
               .should_receive('tell').once()
               .with_args(FatalFailure).mock())

        (flexmock(Worker, work_on=lambda x: None)
         .should_receive('work_on').once()
         .with_args(1).and_raise(ValueError()))

        cr = Crawler.start(ctl, self.tasksource, self.collector,
                           Worker, self.initargs)
        cr.tell(Task(None, 1))
        cr.stop()
        ActorRegistry.stop_all()


class TestController(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_run(self):
        """ test running controller """
        class Worker(object):
            """ dummy """
            def __init__(self, arg):
                """ dummy """
                self.arg = arg

            def work_on(self, task):
                """ dummy """
                print task
                gevent.sleep(1)
                return task + 1

        mocktastiter = flexmock()
        (mocktastiter.should_receive('__iter__')
         .and_yield(1, 2, 3))

        flexmock(Worker).should_call('work_on').once().with_args(1)
        flexmock(Worker).should_call('work_on').once().with_args(2)
        flexmock(Worker).should_call('work_on').once().with_args(3)

        mockwriter = flexmock()
        mockwriter.should_receive('write').once().with_args(2)
        mockwriter.should_receive('write').once().with_args(3)
        mockwriter.should_receive('write').once().with_args(4)
        mockwriter.should_receive('close').once()

        ctl = Controller.start(Worker, (1, 2, 3),
                               mocktastiter, mockwriter, poolsize=3)
        ctl.actor_stopped.wait()

if __name__ == '__main__':
    unittest.main()
