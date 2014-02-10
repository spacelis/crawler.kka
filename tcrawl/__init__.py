#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" An crawler leverage asyncrhonized IO.

File: __init__.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:
    To achieve full asynchronizibility of crawling.

"""
import gzip
from itertools import cycle
from pykka.actor import ActorRef


class Message(dict):

    """ Messages class that used for type match. """

    _next_id = 0

    def __init__(self, sender, identifier=None):
        """@todo: Docstring for __init__.

        :id: @todo
        :sender: @todo
        :returns: @todo

        """
        super(Message, self).__init__()
        if isinstance(sender, ActorRef):
            self.sender = sender
        elif sender is None:
            self.sender = None
        else:
            self.sender = sender.actor_ref
        if identifier:
            self.identifier = identifier
        else:
            self.identifier = Message._next_id
            Message._next_id += 1

    def match(self, handler):
        """@todo: Docstring for match.

        :handler: @todo
        :returns: @todo

        """
        cname = self.__class__.__name__
        if cname in handler:
            return handler[cname](self)
        elif '_' in handler:
            return handler['_'](self)
        else:
            raise ValueError('Unable to find a match for "%s"' % (cname))

    @classmethod
    def N(cls):
        """ Return the class name.
        :returns: @todo

        """
        return cls.__name__


class Task(Message):

    """ A message loaded with a task. """

    def __init__(self, sender, payload):
        """@todo: to be defined1. """
        super(Task, self).__init__(sender)
        self.payload = payload


class Resignition(Message):

    """ A statement of quiting the system. """

    def __init__(self, sender, conf):
        """ init

        :sender: @todo

        """
        super(Resignition, self).__init__(sender)
        self.conf = conf


class Failure(Message):

    """ A notice of unhandled failure. """

    def __init__(self, sender):
        """@todo: to be defined1. """
        super(Failure, self).__init__(sender)


class NoMoreTask(Message):

    """ No more task. """

    def __init__(self, sender):
        """@todo: to be defined1. """
        super(NoMoreTask, self).__init__(sender)


class Done(Message):

    """A message saying a task is done."""

    def __init__(self, sender, task):
        """

        :sender: @todo

        """
        super(Done, self).__init__(sender, task.identifier)


class TaskRequest(Message):

    """ A message requesting a new task. """

    def __init__(self, sender):
        """

        :sender: @todo

        """
        super(TaskRequest, self).__init__(sender)


class Record(Message):

    """ A message conveying the data to be written down. """

    def __init__(self, sender, payload):
        """@todo: to be defined1.

        :payload: @todo
        :identifier: @todo
        :sender: @todo

        """
        super(Record, self).__init__(sender)
        self.payload = payload


class Report(Message):

    """ A message indicating an unusual event. """

    def __init__(self, sender, content):
        """@todo: to be defined1.

        :payload: @todo
        :identifier: @todo
        :sender: @todo

        """
        super(Report, self).__init__(sender)
        self.content = content


class HitRateLimit(Message):

    """ Tell controller that the hitlimit is reached."""

    def __init__(self, sender, nextwindow):
        """

        :nextwindow: @todo

        """
        super(HitRateLimit, self).__init__(sender)
        self._nextwindow = nextwindow
