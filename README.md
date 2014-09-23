# Crawler.KKA

This is an multithreading crawler framework based pykka, an actor system based on gevent (avoiding GIL).

## Setup

You may either clone the repository or download a tarball from github.
Then simply install all the dependencies listed in requirements.
For example:

```bash
git clone https://github.com/spacelis/crawler.kka.git
virtualenv .py27
pip install requirements
```

## How to use

You may refer the examples in the directory ```example```.
A minimum example will only require an implementation of a worker class in which the ```__init__``` will take one argument for configuration and ```work_on``` method for actual crawlling work.
To run any of the examples or your own script for crawlling

```bash
python <yourscript.py>
```

For example, you may want to get some tweets from Twitter:

```bash
python examples/tweet_crawler.py <input> <output>
```

## Concept

The PyKKA system is baiscally a pseudo distributed system where each actor is running on their own.
Different actors can talk to each other though messages.
Thus, it is very easy to remove an actor when one is malfunctioning and put up an new actor for the role.
However, this also increase the complexity of the system.

Gevent is a nice library for IO efficient task scheduling.
It utilizes the system IO calls for managing the running tasks.
So when one task is block for an IO request, other task may use the CPU resources if their IO request is ready to serve.

This is an experiment project for using such an weak coupling framework for crawling system which hopefully can easy to scale up.


## Uitls in the project directory

The project also comes with a patch to the tweepy library for crawling tweets from Twitter.
Tweepy throws away the json string when it finishes parsing it and storing it to a Tweepy object, which sometimes can be annoying.
The patch adds an extra field in the Status object to save the raw json string which do not require a hard patch to the code in Tweepy.
The patch works when it is imported and run after the Tweepy being imported.
For example:

```python
import tweepy
from example.util.tweepy_patch import patchcrawler as __patch_status
__patch_status()
```
An full example can be found in ```examples/tweet_crawler.py```.

## License

MIT LICENSE 2014 spacelis
