#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Crawling the geocode.

File: geocoder.py
Author: SpaceLis
Email: Wen.Li@tudelft.nl
GitHub: http://github.com/spacelis
Description:


"""
from gevent import monkey
monkey.patch_all()

import sys
from geopy import geocoders
import json


from crawler.actors import Controller
from crawler.readers import CSVReader
from crawler.writers import FileWriter

import logging
logging.basicConfig(level=logging.INFO)


class Worker(object):

    """ A worker. """

    def __init__(self, _):
        """@todo: to be defined1.

        :args: @todo

        """
        self.client = geocoders.GoogleV3()

    def work_on(self, x):
        """@todo: Docstring for work_on.

        :x: A dict holding rows in csv
        :returns: The coordinates.

        """
        s = x['Straatnaam']
        n = ('' if x['Huisnummer Melding'] == '0'
             else str(x['Huisnummer Melding']))
        q = ' '.join([s, n, 'Rotterdam Netherlands'])
        try:
            place, (lat, lng) = self.client.geocode(q)
            return ','.join([s, n, '%.7f %.7f' % (lat, lng)])
        except Exception as e:
            logging.exception(e)
            print ','.join([s, n])
            return ''


def test():
    """ test """
    w = Worker('')
    print w.work_on({'Straatnaam': 'FEIJENOORDHAVEN',
                     'Huisnummer Melding': '44'})
    print w.work_on({'Straatnaam': 'FEIJENOORDHAVEN',
                     'Huisnummer Melding': '0'})


def console():
    """ running in console
    :returns: @todo

    """
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Usage: tweet_crawler.py <input> <output>'
        sys.exit()

    controller = Controller.start(Worker, [1],
                                  CSVReader(sys.argv[1]),
                                  FileWriter(sys.argv[2]),
                                  poolsize=15)
    controller.actor_stopped.wait()

if __name__ == '__main__':
    console()
    #test()
