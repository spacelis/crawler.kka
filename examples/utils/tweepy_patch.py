#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" A patch to tweepy for storing original json in Status.

File: tweepy_patch.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""
import types
import sys
from json import dumps


def stack(cls, method, mock):
    """ Patching a method in class. """
    mockee = getattr(cls, method)

    def wrapper(s, *args, **kwargs):
        """ wrapper """
        return mock(s, mockee, *args, **kwargs)

    bak = '__patched__' + method
    setattr(cls, bak, mockee)
    setattr(cls, method, types.MethodType(wrapper, cls))


def preserve_origin(_, mockee, api, json):
    """ preserving the the original json object """
    s = mockee(api, json)
    setattr(s, '_raw', dumps(json))
    return s


def patchStatus():
    """ Patching the tweepy Status objects to make it store the raw json.
    """
    if 'tweepy.models' in sys.modules:
        stack(sys.modules['tweepy.models'].Status, 'parse', preserve_origin)


class ResourceKeeper(object):
    """ Return a resource keeper that will return false
        when all resource have been consumed.

    :returns: Whether there are resource left.

    """
    def __init__(self, limit):
        """ Init resource keeper.

        :limit: A positive number means finite resource
                wile 0 or negative means infinite.

        """
        self.limit = limit
        self.left = limit

    def take(self, num=1, integrity=False):
        """ take resource.

        :num: The number to take away.
        :integrity:
        :returns: @todo

        """
        assert num >= 0
        if not self.limit:
            return True

        if integrity:
            ret = (self.left - num >= 0)
        else:
            ret = (self.left > 0)
        if self.left > 0:
            self.left -= num
        return ret

    def empty(self):
        """@todo: Docstring for empty.
        :returns: @todo

        """
        return self.left <= 0


def iter_scoll(api, limit, *args, **kwargs):
    """ Iterating through pages of Twitter API.

    :api: The api to use from Tweepy
    :limit: The max number of tweets to scroll back in time.
    :*args: Args for the tweepy API.
    :**kwargs: Key word args for the tweepy API.
    :yields: A status object from Tweepy.

    """
    _has_more = True
    res = ResourceKeeper(limit)
    if 'count' not in kwargs:
        kwargs['count'] = 100
    while _has_more:
        _has_more = False
        for s in api(*args, **kwargs):
            _has_more = True
            max_id = s.id
            if not res.take():
                break
            yield s
        if res.empty():
            break
        kwargs['max_id'] = max_id - 1
