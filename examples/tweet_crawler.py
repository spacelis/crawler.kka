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
import time

import tweepy as tw
from tcrawl.actors import Controller
from tcrawl.readers import CSVReader
from tcrawl.writers import FileWriter
from tcrawl import IgnorableError
from tcrawl import RecoverableError

from tcrawl.api_patch import patch as __patch_status
__patch_status()

import logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class Worker(object):

    """ A worker. """

    def __init__(self, cred):
        """@todo: to be defined1.

        :args: @todo

        """
        self._oauthhl = tw.OAuthHandler(cred['consumer_key'],
                                        cred['consumer_secret'])
        self._oauthhl.set_access_token(cred['access_token_key'],
                                       cred['access_token_secret'])
        self._client = tw.API(self._oauthhl)
        assert self._client.verify_credentials(), cred

    def work_on(self, param):
        """@todo: Docstring for work_on.

        :tid: @todo
        :returns: @todo

        """
        try:
            ret = self._client.get_status(id=param['tid'])
            _logger.debug(ret)
            return ret._raw
        except tw.TweepError as e:
            if e.response.status == 429:
                nxwin = e.response.getheader('X-Rate-Limit-Reset')
                retry_in = time.time() - nxwin + 5
                raise RecoverableError(e, retry_in)
            raise IgnorableError(e)


def console():
    """ running in console
    :returns: @todo

    """
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Usage: tweet_crawler.py <input> <output>'
        sys.exit()

    with open('cred.yaml') as fin:
        cred = yaml.load(fin)
    controller = Controller.start(Worker, cred,
                                  CSVReader(sys.argv[1]),
                                  FileWriter(sys.argv[2]))
    controller.actor_stopped.wait()

if __name__ == '__main__':
    console()
