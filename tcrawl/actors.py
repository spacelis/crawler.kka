#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" A module contains all actors.

File: actors.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""
from itertools import cycle
#from pykka.actor import ThreadingActor as _Actor
from pykka.gevent import GeventActor as _Actor
from gevent.event import Event as _Event

from tcrawl import NoMoreTask
from tcrawl import Task
from tcrawl import TaskRequest
from tcrawl import Record
from tcrawl import RecoverableError
from tcrawl import Resignition
from tcrawl import Failure


import logging
_logger = logging.getLogger(__name__)


class Controller(_Actor):

    """ A Controller is a coordinator of a crawling process. """

    def __init__(self, worker, initargs, task_iter, output, poolsize=10):
        """ Setup the actor system and should be called through
            Controller.start()

        """
        super(Controller, self).__init__()
        self._tasksource = None
        self._collector = None

        self._output = output
        self._worker = worker
        self._worker_initargs = initargs
        self._task_iter = task_iter
        self._poolsize = poolsize
        self.refpool = []

    def on_start(self):
        """ Start the whole setup actor system.
        """
        self._tasksource = TaskSource.start(self.actor_ref, self._task_iter)
        self._collector = Collector.start(self.actor_ref, self._output)
        self.refpool = [Crawler.start(self.actor_ref,
                                      self._tasksource,
                                      self._collector,
                                      self._worker, args)
                        for _, args in zip(range(self._poolsize),
                                           cycle(self._worker_initargs))]

    def on_receive(self, msg):
        """ Processing the received messages.

        :msg: @todo
        :returns: @todo

        """
        return msg.match({
            Resignition.N(): self.handle_resignition,
            Failure.N(): self.handle_child_failure,
            '_': lambda msg: None
        })

    def handle_ratelimit(self, msg):
        """@todo: Docstring for handle_ratelimit.

        :arg1: @todo
        :returns: @todo

        """
        pass

    def handle_child_failure(self, msg):
        """ Handling failures from child actors.

        :msg: @todo
        :returns: @todo

        """
        if msg.sender.actor_class.__name__ == 'Crawler':
            msg.sender.stop()
            self.refpool.remove(msg.sender)
            self.refpool.append(
                Crawler.start(self, self._tasksource, self._collector,
                              *msg.conf))

    def handle_resignition(self, msg):
        """@todo: Docstring for handle_resignition.

        :msg: @todo
        :returns: @todo

        """
        if msg.sender.actor_class.__name__ == 'Crawler':
            self.refpool.remove(msg.sender)
            msg.sender.stop()
            if len(self.refpool):
                self._tasksource.stop()
                self._collector.stop()
                self._tasksource.actor_stopped.wait()
                self._collector.actor_stopped.wait()
                self.stop()


class TaskSource(_Actor):

    """Docstring for TaskSource. """

    def __init__(self, controller, taskset):
        """@todo: to be defined1. """
        super(TaskSource, self).__init__()
        self._taskset = iter(taskset)
        self._controller = controller
        self._resigned = _Event()
        self._last_assigned = None

    def on_receive(self, msg):
        """ Handling messages.

        :msg: @todo
        :returns: @todo

        """
        return msg.match({
            TaskRequest.N(): lambda msg: self.send_task(msg.sender),
            '_': lambda msg: None
        })

    def send_task(self, receiver):
        """ Send a task.

        :msg: @todo
        :returns: @todo

        """
        try:
            task = self._taskset.next()
            receiver.tell(Task(self, task))
            self._last_assigned = task
        except StopIteration:
            receiver.tell(NoMoreTask(self))

    def on_stop(self):
        """
        :returns: @todo

        """
        print 'Stopped TaskSource'

    def on_failure(self, exception_type, exception_value, traceback):
        """ Deal with failure """
        _logger('[%s:%s] Last assigned: %s',
                self.__class__.__name__,
                self.actor_urn,
                self._last_assigned)
        self._controller.tell(Failure(self))


class Crawler(_Actor):

    """ The crawler is responsible for receiving work and crawling"""

    def __init__(self, controller, tasksource, collector, worker, initargs):
        """@todo: to be defined1. """
        super(Crawler, self).__init__()
        self._controller = controller
        self._collector = collector
        self._tasksource = tasksource
        self._worker = worker(initargs)
        self._performance = dict()
        self._conf = (worker, initargs)
        self._current_task = None

    def on_start(self):
        """ Starting the cralwer.
        :returns: @todo

        """
        self._tasksource.tell(TaskRequest(self))

    def on_receive(self, msg):
        """ Handling received messages.

        :msg: @todo
        :returns: @todo

        """
        return msg.match({
            Task.N(): lambda msg: self.work(msg.payload),
            NoMoreTask.N(): lambda msg: self.handle_nomoretask(),
            '_': lambda msg: None
        })

    def handle_nomoretask(self):
        """ Stop self if no more task.
        :returns: @todo

        """
        _logger.info('[%s:%s] Exit Successfully with no more tasks.',
                     self.__class__.__name__,
                     self.actor_urn)
        self._controller.tell(Resignition(self, self._conf))

    def work(self, task):
        """ Crawl the task.

        :msg: @todo
        :returns: @todo

        """
        try:
            self._current_task = task
            ret = self._worker.work_on(task)
            self._collector.tell(Record(self, ret))
            self._tasksource.tell(TaskRequest(self))
        except RecoverableError as e:  # pylint: disable=W0703
            self._controller.tell(Failure(self, e.message))
            self._performance['fails'] = self._performance.get('fails', 0) + 1
            self.actor_ref.tell(Task(self, task))

    def on_failure(self, exception_type, exception_value, traceback):
        """ Deal with thing unforeseen failure. """
        _logger.error('[%s:%s] Attempt Fails: %s',
                      self.__class__.__name__,
                      self.actor_urn,
                      self._current_task)
        _logger.exception(exception_value)
        self._controller.tell(Failure(self))


class Collector(_Actor):

    """Docstring for Collector. """

    def __init__(self, controller, writable):
        """@todo: to be defined1. """
        super(Collector, self).__init__()
        self._writable = writable
        self._controller = controller
        self._last_written = None

    def on_receive(self, msg):
        """ Handling received msg.

        :msg: @todo
        :returns: @todo

        """
        return msg.match({
            Record.N(): self.write,
            '_': lambda msg: None
        })

    def write(self, msg):
        """ Write down the msg.

        :msg: @todo
        :returns: @todo

        """
        self._writable.write(msg.payload)
        self._last_written = msg.payload

    def on_stop(self):
        """ Clean up for stop self.
        :returns: @todo

        """
        print 'Collector stopping'
        self._writable.close()

    def on_failure(self, exception_type, exception_value, traceback):
        """@todo: Docstring for on_failure.

        :exception_type: @todo
        :exception_value: @todo
        :traceback: @todo
        :returns: @todo

        """
        _logger.error('[%s:%s] Failed after: %s',
                      self.__class__.__name__,
                      self.actor_urn,
                      self._last_written)
        _logger.exception(exception_value)
        self._controller.tell(Failure(self))
        self._writable.close()
