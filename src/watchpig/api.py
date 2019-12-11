# coding=utf-8
import time
import os
import re
from watcher import Watcher
from painter import paint
from emoji_base import EMOJI_MAP

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


def multi_watch(args):
    gens = []
    config = configparser.ConfigParser()
    watch_path = os.environ.get('WATCHPIG')
    if watch_path is None:
        print("WATCHPIG未提供")
        return
    config.read(watch_path)
    paint(u"程序启动::FOREGROUND::celeste|| ::EMOJI::pig|| start...")
    for name in config.sections():
        paint(u'项目名称::FOREGROUND::celeste|| %s::FOREGROUND::yellow|| watching ...' % name)
        watch_dict = {}
        for key, value in config[name].items():
            watch_dict[key] = value
        excludes = watch_dict['excludes'].split('|') if watch_dict.get('excludes') else None
        gen = Watcher(watch_dict['path'], excludes=excludes, project=name).auto_reload(watch_dict['action'])
        gens.append(gen)
    while True:
        for g in gens:
            next(g)
        time.sleep(1)


def search_emoji(args):
    for name, emoji in EMOJI_MAP.items():
        result = re.search(args.search, name, re.IGNORECASE)
        if result:
            start = result.start()
            end = result.end()
            paint("%s||%s::FOREGROUND::red||%s|| %s" % (name[:start], name[start:end], name[end:], emoji))
