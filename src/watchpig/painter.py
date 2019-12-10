# coding=utf-8


BACKGROUND = {
    "black": u"\033[40;37m{text}\033[0m",
    "red": u"\033[41;37m{text}\033[0m",
    "green": u"\033[42;37m{text}\033[0m",
    "yellow": u"\033[43;37m{text}\033[0m",
    "blue": u"\033[44;37m{text}\033[0m",
    "purple": u"\033[45;37m{text}\033[0m",
    "celeste": u"\033[46;37m{text}\033[0m",
    "white": u"\033[47;30m{text}\033[0m",
}

FOREGROUND = {
    "black": u"\033[30m{text}\033[0m",
    "red": u"\033[31m{text}\033[0m",
    "green": u"\033[32m{text}\033[0m",
    "yellow": u"\033[33m{text}\033[0m",
    "blue": u"\033[34m{text}\033[0m",
    "purple ": u"\033[35m{text}\033[0m",
    "celeste": u"\033[36m{text}\033[0m",
    "white": u"\033[37m{text}\033[0m"
}

EMOJI = {
    "pig": u'🐷',
    "time": u'🕒',
    "separator": u'➖',
    'succeed': u'😃',
    'failed': u'😡',
    "run": u'🚀',
    "change": u'📝',

    "translate": u'💬',
    "dashboard": u'🌏',
    "horizon": u'🌏',
    "novaclient": u'🌏',
    "nova": u'🌟',
    "glance": u'💿',
    "cinder": u'💾',
}


def _paint(text, *args):
    if len(args) < 2:
        return text
    kind, name = args[:2]
    text = eval(kind)[name].format(text=text)
    return _paint(text, *args[2:])


# import pysnooper
# @pysnooper.snoop(max_variable_length=None)
def paint(short_code, repeat=1):
    result = []
    units = short_code.split("||")

    # # cover space in text
    # for index, unit in enumerate(pre_process):
    #     if "::" not in unit:
    #         continue
    #     units.append(''.join(pre_process[:index+1]))
    for unit in units:
        result.append(_paint(*unit.split("::")))
    print(' '.join(result) * repeat)
    # return ' '.join(result)



if __name__ == '__main__':
    demo = u'\u9879\u76ee\u540d\u79f0::FOREGROUND::celeste||::EMOJI::translate||openstack_dashboard_locale::FOREGROUND::yellow||watching ...'
    print(paint(demo))
