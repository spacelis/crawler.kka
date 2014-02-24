#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Testing Tweepy.

File: test_tweepypatch.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""

from crawler.utils.tweepy_patch import ResourceKeeper
from crawler.utils.tweepy_patch import iter_scoll


import unittest


class TestTweepyPactch(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_resourcekeeper(self):
        r = ResourceKeeper(5)
        self.assertTrue(r.take())
        self.assertFalse(r.empty())
        self.assertEqual(r.left, 4)
        self.assertTrue(r.take(2))
        self.assertTrue(r.take(2))
        self.assertFalse(r.take())
        self.assertTrue(r.empty())
        r = ResourceKeeper(5)
        self.assertFalse(r.take(6, True))
