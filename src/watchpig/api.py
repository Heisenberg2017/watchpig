from monitor.watcher import Watcher
import time
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


def multi_watch(args):
    gens = []
    config = configparser.ConfigParser()
    config.read('conf/monitor.conf')
    for name in config.sections():
        print('-----[%s]-----' % name)
        watch_dict = {}
        for key, value in config[name].items():
            print("%s: %s" % (key, value))
            watch_dict[key] = value
        excludes = watch_dict['excludes'].split('|') if watch_dict.get('excludes') else None
        gen = Watcher(watch_dict['path'], excludes=excludes, project=name).auto_reload(watch_dict['action'])
        gens.append(gen)
    while True:
        for g in gens:
            next(g)
        time.sleep(1)
