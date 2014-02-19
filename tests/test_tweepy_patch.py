#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Testing tweepy_patch.

File: test_tweepy_patch.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""
# pylint: disable=R0904
import unittest


class TestStack(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_stack(self):
        """ test_stack """
        from tcrawl.api_patch import stack

        class ATestClase(object):  # pylint: disable=R0903

            """Docstring for ATestClase. """

            def __init__(self, api):
                """@todo: to be defined1.

                :api: @todo

                """
                self._api = api

        class AnotherClass(ATestClase):

            """Docstring for AnotherClass. """

            @classmethod
            def parse(cls, api, x):
                """@todo: Docstring for parse.

                :x: @todo
                :returns: @todo

                """
                s = cls(api)
                setattr(s, 'x', x)
                return s

            def objfunc(self):
                """ dummy """
                pass

        def mockfunc(_, mockee, api, x):
            """ dummy """
            s = mockee(api, x)
            setattr(s, 'y', x+1)
            return s
        stack(AnotherClass, 'parse', mockfunc)
        s = AnotherClass.parse('testapi', 10)
        self.assertEqual(s.y, 11)  # pylint: disable=E1101

    def test_patched_status(self):
        """@todo: Docstring for test_patched_status.
        :returns: @todo

        """
        from tweepy.models import Status
        from tcrawl.tweepy_patch import patch
        patch()
        s = Status.parse('test_api', {'a': 1, 'b': 2})
        # pylint: disable=E1101,W0212
        self.assertEqual(s._raw, '{"a": 1, "b": 2}')
        self.assertEqual(s.a, 1)
        self.assertEqual(s.b, 2)
