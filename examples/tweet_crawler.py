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

import yaml
from tcrawl.actors import Controller
import tweepy as tw


class Worker(object):

    """ A worker. """

    def __init__(self, creds):
        """@todo: to be defined1.

        :args: @todo

        """
        self._client = tw.API(**creds)

    def work_on(self, tid):
        """@todo: Docstring for work_on.

        :tid: @todo
        :returns: @todo

        """
        return self._client.get_status(id=tid)


if __name__ == '__main__':

    with open('.cred.yaml') as fin:
        cred = yaml.load(fin)
    output = Collector(sys.argv[2])
    controller = Controller.start(Worker, cred,
                                  CSVReader(sys.argv[1]), output)
    controller.actor_stopped.wait()
