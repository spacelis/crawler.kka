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
#from gevent import monkey
#monkey.patch_all()

import sys
import yaml
import time

import tweepy as tw
#from crawler.actors import Controller
#from crawler.readers import CSVReader
#from crawler.writers import FileWriter
#from crawler import IgnorableError
#from crawler import RecoverableError

from crawler.utils.tweepy_patch import patch as __patch_status
from crawler.utils.tweepy_patch import iter_scoll
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
            for s in iter_scoll(self._client.search, 1000,
                                q=param['hashtag']):
                yield s._raw
        except tw.TweepError as e:
            if e.response.status == 429:
                nxwin = float(e.response.getheader('X-Rate-Limit-Reset'))
                retry_in = nxwin + 5 - time.time()
                time.sleep(retry_in)
            #_logger.warn('Failed at %s', param)
            #raise IgnorableError(e)


#def console():
    #""" running in console
    #:returns: @todo

    #"""
    #if len(sys.argv) != 3:
        #print >> sys.stderr, 'Usage: tweet_crawler.py <input> <output>'
        #sys.exit()

    #with open('cred.yaml') as fin:
        #cred = yaml.load(fin)
    #controller = Controller.start(Worker, cred,
                                  #CSVReader(sys.argv[1]),
                                  #FileWriter(sys.argv[2]))
    #controller.actor_stopped.wait()


def simple():
    """ A simple version of crawler.
    """
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Usage: tweet_crawler.py <input> <output>'
        sys.exit()
    with open('cred.yaml') as fin:
        w = Worker(yaml.load(fin)[0])
    with open(sys.argv[1]) as fin:
        with open(sys.argv[2], 'a') as fout:
            for line in fin:
                for s in w.work_on({'hashtag': line.strip()}):
                    fout.write(s)
                    fout.write('\n')


if __name__ == '__main__':
    simple()
