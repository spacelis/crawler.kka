#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" A module contains all actors.

File: actors.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""
# pylint: disable=R0913
from itertools import cycle
from collections import defaultdict
#from pykka.actor import ThreadingActor as _Actor
from pykka.gevent import GeventActor as _Actor
from gevent.event import Event as _Event
from gevent import sleep

from crawler import NoMoreTask
from crawler import Task
from crawler import TaskRequest
from crawler import Record
from crawler import RecoverableError
from crawler import IgnorableError
from crawler import Resignition
from crawler import NonFatalFailure
from crawler import Retire


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
        self.manager = defaultdict(int)

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
            NonFatalFailure.N(): self.handle_nonfatal_failure,
            Retire.N(): self.handle_retire,
            '_': lambda msg: None
        })

    def handle_nonfatal_failure(self, msg):
        """ Handling failures from child actors.

        :msg: @todo
        :returns: @todo

        """
        if msg.sender.actor_class.__name__ == 'Crawler':
            _logger.debug(msg)
            self.manager[msg.sender.actor_urn] += 1

    def handle_resignition(self, msg):
        """ Handling failures from child actors.

        :msg: @todo
        :returns: @todo

        """
        if msg.sender.actor_class.__name__ == 'Crawler':
            self.refpool.remove(msg.sender)
            _logger.debug(msg)
            self.refpool.append(
                Crawler.start(self.actor_ref,
                              self._tasksource,
                              self._collector,
                              *msg.conf))

    def handle_retire(self, msg):
        """@todo: Docstring for handle_resignition.

        :msg: @todo
        :returns: @todo

        """
        if msg.sender.actor_class.__name__ == 'Crawler':
            self.refpool.remove(msg.sender)
            _logger.info('%s Crawler left', len(self.refpool))
            msg.sender.stop()
            if len(self.refpool) == 0:
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
            _logger.debug('Send out %s', task)
            self._last_assigned = task
        except StopIteration:
            receiver.tell(NoMoreTask(self))

    def on_failure(self, exception_type, exception_value, traceback):
        """ Deal with failure """
        _logger('Last assigned: %s | %s (%s)',
                self._last_assigned,
                self.__class__.__name__,
                self.actor_urn)
        self._controller.tell(Resignition(self, exception_value,
                                          traceback, (None, None)))


class Crawler(_Actor):

    """ The crawler is responsible for receiving work and crawling"""

    def __init__(self, controller, tasksource, collector, worker, initargs):
        """@todo: to be defined1. """
        super(Crawler, self).__init__()
        self._controller = controller
        self._collector = collector
        self._tasksource = tasksource
        self._worker = None
        self._performance = dict()
        self._conf = (worker, initargs)
        self._current_task = None

    def on_start(self):
        """ Starting the cralwer.
        :returns: @todo

        """
        _logger.info('Crawler started [%s]', self.actor_urn)
        self._worker = self._conf[0](self._conf[1])
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
        _logger.info('Crawler retired [%s]', self.actor_urn)
        self._controller.tell(Retire(self))

    def work(self, task):
        """ Crawl the task.

        :msg: @todo
        :returns: @todo

        """
        _logger.debug('Receive task: %s', task)
        try:
            self._current_task = task
            ret = self._worker.work_on(task)
            self._collector.tell(Record(self, ret))
            self._tasksource.tell(TaskRequest(self))
            _logger.debug('Succeeded task: %s', task)
        except RecoverableError as e:  # pylint: disable=W0703
            _logger.warn('RecoverableError %s', e)
            self._controller.tell(NonFatalFailure(self, e))
            self._performance['fails'] = self._performance.get('fails', 0) + 1
            sleep(e.retry_in)
            self.actor_ref.tell(Task(self, task))
        except IgnorableError as e:
            _logger.debug('IgnorableError %s', e)
            self._controller.tell(NonFatalFailure(self, e))
            self._performance['fails'] = self._performance.get('fails', 0) + 1
            self._tasksource.tell(TaskRequest(self))

    def on_failure(self, exception_type, exception_value, traceback):
        """ Deal with thing unforeseen failure. """
        _logger.error('Crawler Failed: %s [%s]',
                      self._current_task,
                      self.actor_urn)
        _logger.exception(exception_value)
        self._controller.tell(Resignition(self, exception_value,
                                          traceback, self._conf))


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
        self._writable.close()

    def on_failure(self, exception_type, exception_value, traceback):
        """@todo: Docstring for on_failure.

        :exception_type: @todo
        :exception_value: @todo
        :traceback: @todo
        :returns: @todo

        """
        _logger.error('Write Failed: %s [%s]',
                      self._last_written,
                      self.actor_urn)
        _logger.exception(exception_value)
        self._writable.close()
        self._controller.tell(Resignition(self, exception_value,
                                          traceback, (None, None)))
