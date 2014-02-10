#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" A module for common readers for crawlers.

File: readers.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""
import csv


class CSVReader(object):

    """A reader class for reading csv file with headings. """

    def __init__(self, filename):
        """@todo: to be defined1.

        :filename: @todo

        """
        self._filename = filename
        self._reader = csv.DictReader(open(filename))

    def __iter__(self):
        for item in self._reader:
            yield item
