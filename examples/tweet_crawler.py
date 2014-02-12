#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Crawler for retreiving tweets by ids.

File: tweet_crawler.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:
    Retreiving tweets by ids.

"""
from gevent import monkey
monkey.patch_all()

import sys
import yaml
from tcrawl.actors import Controller
from tcrawl.readers import CSVReader
from tcrawl.writers import FileWriter
import tweepy as tw
import logging
logging.basicConfig(level=logging.DEBUG)


class Worker(object):

    """ A worker. """

    def __init__(self, creds):
        """@todo: to be defined1.

        :args: @todo

        """
        self._oauthhl = tw.OAuthHandler(creds['consumer_key'],
                                        creds['consumer_secret'])
        self._oauthhl.set_access_token(creds['access_token_key'],
                                       creds['access_token_secret'])
        self._client = tw.API(self._oauthhl)
        assert self._client.verify_credentials()

    def work_on(self, tid):
        """@todo: Docstring for work_on.

        :tid: @todo
        :returns: @todo

        """
        try:
            return self._client.get_status(id=tid)
        except (TweepyError, AssertionError):
            raise IgnorableError()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Usage: tweet_crawler.py <input> <output>'
        sys.exit()

    with open('cred.yaml') as fin:
        cred = yaml.load(fin)
    controller = Controller.start(Worker, cred,
                                  CSVReader(sys.argv[1]),
                                  FileWriter(sys.argv[2]))
    controller.actor_stopped.wait()
