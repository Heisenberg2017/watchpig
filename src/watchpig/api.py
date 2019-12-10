# coding=utf-8
from watcher import Watcher
from painter import paint
import time

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


def multi_watch(args):
    gens = []
    config = configparser.ConfigParser()
    config.read('/root/watchpig/monitor.conf')
    paint(u"程序启动::FOREGROUND::celeste||::EMOJI::pig||start...")
    for name in config.sections():
        paint(u'项目名称::FOREGROUND::celeste||%s::FOREGROUND::yellow||watching ...' % name)
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
