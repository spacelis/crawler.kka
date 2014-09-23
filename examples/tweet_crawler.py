#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Crawler for retreiving tweets by ids.

File: tweet_crawler.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:
    This is an example of actor based crawler system.
    To run this script you need to have both pairs of key and secret for an application registered on Twitter and a user authoring in the application.
    Basically, you register an application on Twitter and get the access_token for yourself in the application.
    Check out http://dev.twitter.com
    Then the tokens should be put in a file called `creds.yaml' which is a yaml format file for all the keys.
    It should looks like:

```
-
        consumer_key: xxxx
        consumer_secret: yyyy
        access_token_key: 9999999-zzzz
        access_token_secret: mmmm
```
    Make sure the creds.yaml is in the same directory where you run your script (not where the script is stored).
    Usage:
        tweet_crawler.py <input> <output>

    The input is a csv file with one colmn called tid which is the tweet id.
    The output will be a file with each line a json string representing a tweet.
"""


from gevent import monkey
monkey.patch_all()

import sys
import yaml
import time

import tweepy as tw
from crawler.actors import Controller
from crawler.readers import CSVReader
from crawler.writers import FileWriter
from crawler import IgnorableError
from crawler import RecoverableError

from examples.utils.tweepy_patch import patchStatus
patchStatus()

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
_logger = logging.getLogger(__name__)


class Worker(object):

    """ A worker. """

    def __init__(self, cred):
        """ Init the worker with the keys.

        :cred: an dictionary providing both key-secret pairs for an application and an authorized user.
        """
        self._oauthhl = tw.OAuthHandler(cred['consumer_key'],
                                        cred['consumer_secret'])
        self._oauthhl.set_access_token(cred['access_token_key'],
                                       cred['access_token_secret'])
        self._client = tw.API(self._oauthhl)
        assert self._client.verify_credentials(), cred

    def work_on(self, param):
        """ Request a tweet from Twitter with an tweet id.

        :param: an dictionary have a field called 'tid' and its value is a tweet id in string.
        :returns: a json string returned by Twitter

        """
        try:
            ret = self._client.get_status(id=param['tid'])
            _logger.debug(ret)
            return ret._raw
        except tw.TweepError as e:
            if e.response:
                if e.response.status == 429:
                    nxwin = float(e.response.getheader('X-Rate-Limit-Reset'))
                    retry_in = nxwin + 5 - time.time()
                    raise RecoverableError(e, retry_in)
                elif e.message[0]['code'] in [63, 34, 179]:
                    # deleted or protected tweets
                    raise IgnorableError(e)
            _logger.error('Failed at %s', param)
            raise e


def console():
    """ Handling argumant parsing when running from a console.
    """
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Usage: tweet_crawler.py <input> <output>'
        sys.exit()

    with open('creds.yaml') as fin:
        creds = yaml.load(fin)
    controller = Controller.start(Worker, creds,
                                  CSVReader(sys.argv[1]),
                                  FileWriter(sys.argv[2]))
    controller.actor_stopped.wait()

if __name__ == '__main__':
    console()
