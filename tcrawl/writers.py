#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Module for common writers.

File: writers.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""
import json
import gzip


class FileWriter(object):

    """ A writable for writing into plain files. """

    def __init__(self, filename, mode='wb', compressed=False):
        """ Construct a writable to write into plain file.

        :filename: @todo

        """
        self._filename = filename
        if compressed:
            self._file = gzip.open(filename, mode)
        else:
            self._file = open(filename, mode)

    def write(self, payload):
        """ Writting payload to file.

        :payload: @todo
        :returns: @todo

        """
        self._file.write(payload.encode('utf-8'))
        self._file.write('\n')

    def close(self):
        """ Close the writable.
        :returns: @todo

        """
        self._file.flush()
        self._file.close()


class JsonEncoder(object):

    """Docstring for JsonFileWriter. """

    def __init__(self, ostream):
        """
        :ostream: A writable
        """
        self._ostream = ostream

    def write(self, payload):
        """ Writing the payload.

        :payload: @todo
        :returns: @todo

        """
        self._ostream.write(json.dumps(payload))

    def close(self):
        """ Close this stream.
        :returns: @todo

        """
        self._ostream.close()
