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


def patch():
    if 'tweepy.models' in sys.modules:
        stack(sys.modules['tweepy.models'].Status, 'parse', preserve_origin)
