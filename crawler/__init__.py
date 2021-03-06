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
    __slots__ = ['sender', 'identifier', 'kind']

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
        self.kind = self.__class__.__name__

    def match(self, handler):
        """@todo: Docstring for match.

        :handler: @todo
        :returns: @todo

        """
        cname = self.kind
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

    def __str__(self):
        """ Return a string
        :returns: @todo

        """
        return "%s from %s [%s]" % (self.N(),
                                    self.sender.actor_class.__name__,
                                    self.sender.actor_urn)


class Task(Message):

    """ A message loaded with a task. """
    __slots__ = ['payload']

    def __init__(self, sender, payload):
        super(Task, self).__init__(sender)
        self.payload = payload


class NoMoreTask(Message):

    """ No more task. """

    def __init__(self, sender):
        super(NoMoreTask, self).__init__(sender)


class Done(Message):

    """A message saying a task is done."""

    def __init__(self, sender, task):
        super(Done, self).__init__(sender, task.identifier)


class TaskRequest(Message):

    """ A message requesting a new task. """

    def __init__(self, sender):
        super(TaskRequest, self).__init__(sender)


class Record(Message):

    """ A message conveying the data to be written down. """
    __slots__ = ['payload']

    def __init__(self, sender, payload):
        super(Record, self).__init__(sender)
        self.payload = payload


class Report(Message):

    """ A message indicating an unusual event. """
    __slots__ = ['content']

    def __init__(self, sender, content):
        super(Report, self).__init__(sender)
        self.content = content


class NonFatalFailure(Message):

    """ A notice of unhandled failure. """
    __slots__ = ['err']

    def __init__(self, sender, err):
        super(NonFatalFailure, self).__init__(sender)
        self.err = err

    def __str__(self):
        """@todo: Docstring for __str__.
        :returns: @todo

        """
        return "%s : %s" % (super(NonFatalFailure, self).__str__(),
                            self.err)


class Resignition(Message):

    """ A notice that the crawler is hit by sever problems. """
    __slots__ = ['err', 'stack', 'conf']

    def __init__(self, sender, err, stack, conf):
        """@todo: to be defined1. """
        super(Resignition, self).__init__(sender)
        self.err = err
        self.stack = stack
        self.conf = conf

    def __str__(self):
        """@todo: Docstring for __str__.
        :returns: @todo

        """
        return "%s: %s\n%s\n%s" % (super(Resignition, self).__str__(),
                                   self.conf, self.err, self.stack)


class Retire(Message):

    """ A notice that the crawler is hit by sever problems. """

    def __str__(self):
        """@todo: Docstring for __str__.
        :returns: @todo

        """
        return "Retired: %s" % (self.sender.actor_urn)


class RecoverableError(Exception):

    """ Tell controller that there is a non-fatal error. """
    __slots__ = ['err', 'retry_in']

    def __init__(self, err, retry_in=10):
        super(RecoverableError, self).__init__()
        self.retry_in = retry_in
        self.err = err

    def __str__(self):
        """@todo: Docstring for __str__.
        :returns: @todo

        """
        return "Retry in %s because %s" % (self.retry_in, str(self.err))


class IgnorableError(Exception):

    """ Tell controller that there is a non-fatal error. """
    __slots__ = ['err']

    def __init__(self, err):
        super(IgnorableError, self).__init__()
        self.err = err

    def __str__(self):
        """@todo: Docstring for __str__.
        :returns: @todo

        """
        return str(self.err)
