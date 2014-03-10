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
import re
import requests


from crawler.actors import Controller
from crawler.readers import CSVReader
from crawler.writers import FileWriter

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
COORD = re.compile(r'<gml:pos dimension="2">([\d.]+ [\d.]+)</gml:pos>')


class Worker(object):

    """ A worker. """

    def __init__(self, _):
        """@todo: to be defined1.

        :args: @todo

        """
        pass

    def work_on(self, x):
        """@todo: Docstring for work_on.

        :x: A dict holding rows in csv
        :returns: The coordinates.

        """
        s = x['Straatnaam']
        n = ('' if x['Huisnummer Melding'] == '0'
             else str(x['Huisnummer Melding']))
        q = {'zoekterm': ' '.join([s, n, 'Rotterdam'])}
        try:
            ret = requests.get(
                'http://geodata.nationaalgeoregister.nl/geocoder/Geocoder',
                params=q
            )

            return ','.join([s, n] +
                            COORD.search(ret.text).group(1).split(' '))
        except Exception as e:
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
