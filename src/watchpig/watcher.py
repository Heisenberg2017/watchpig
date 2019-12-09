# coding=utf-8

import os
import sys
import time
import datetime
import itertools
import commands
from collections import namedtuple
import output

# TODO: 目前先采用os.stat的形式来判断文件是否有修改，仅处理修改操作，后续可以考虑参考watchdog的方式

# file_map = {}

ChangeTrace = namedtuple('ChangeTrace', 'changed filepath detail format_print')
ChangDetail = namedtuple('ChangDetail', 'filename lines stamp change_lines isdir is_change')


def get_isdir(filename):
    return os.path.isdir(filename)


def get_line_counts(filename):
    count = 0
    if not os.path.isdir(filename):
        count = sum(1 for _ in open(filename))
    return count


def get_stamp(f_path):
    return os.stat(f_path).st_mtime


def get_change_lines(trace_detail, stamp):
    if trace_detail.stamp == stamp:
        return 0

    if trace_detail.isdir:
        return 0

    old_lines = trace_detail.lines
    new_lines = get_line_counts(trace_detail.filename)
    change_lines = new_lines - old_lines
    return change_lines


def file_exclude(path, excludes):
    # 排除不需要跟踪的文件
    import re
    for exclude in excludes:
        if re.search(exclude, path):
            return True
    return False


def recursion_file(filepath, excludes=None):
    g = os.walk(filepath)
    for path, dirs, files in g:
        for d in itertools.chain(dirs, files):
            f_path = os.path.join(path, d)
            # 目录需要添加后缀
            f_path = "%s/" % f_path if os.path.isdir(f_path) else f_path
            # 排除不需要跟踪的文件
            if excludes and file_exclude(f_path, excludes):
                continue
            yield f_path


class Output(output.OutputBase):
    def write(self, obj):
        print(obj)


class Watcher:

    def __init__(self, filepath, test=False, excludes=None, project=None):
        self.file_map = {}
        self.excludes = excludes
        self.filepath = filepath
        self.is_change = False
        self.project = project
        self.output = Output()
        self.test = test
        self._init()

    def _init(self):
        for f_path in recursion_file(self.filepath, self.excludes):
            self.file_map[f_path] = ChangDetail(
                stamp=get_stamp(f_path),
                lines=get_line_counts(f_path),
                change_lines=0,
                filename=f_path,
                isdir=get_isdir(f_path),
                is_change=False
            )

    def changed(self, filename, stamp):

        return stamp != self.file_map[filename].stamp

    def gen_change_print(self, change_details):
        max_len = max([len(change_detail.filename) for change_detail in change_details])
        mid_index = max_len / 3
        # max_len = 80
        pre_str = ''
        mid_str = '...'
        tail_str = ''
        split_str = '     | '
        add_str = '\033[32m+\033[0m'
        reduce_str = '\033[31m-\033[0m'
        for change_detail in change_details:
            if change_detail.isdir:
                continue
            print_str = ''
            symbol_str = ''
            if change_detail.change_lines > 0:
                symbol_str = '%s %s' % (add_str, change_detail.change_lines)
            elif change_detail.change_lines < 0:
                symbol_str = '%s %s' % (reduce_str, - change_detail.change_lines)
            else:
                symbol_str = '  %s' % change_detail.change_lines

            if len(change_detail.filename) > max_len:
                print_str += change_detail.filename[:mid_index] + mid_str + change_detail.filename[
                                                                            mid_index:max_len] + split_str + symbol_str
            else:
                print_str = change_detail.filename[:mid_index] + change_detail.filename[mid_index:] + ' ' * (
                        max_len - len(change_detail.filename)) + split_str + symbol_str

            self.output(print_str)

    def change_trace_with_new_file(self, f_path):
        self.file_map[f_path] = None
        file_change = True
        lines = get_line_counts(f_path)
        change_detail = ChangDetail(
            stamp=get_stamp(f_path),
            lines=lines,
            filename=f_path,
            isdir=get_isdir(f_path),
            change_lines=lines,
            is_change=file_change
        )
        self.file_map[f_path] = change_detail
        if not file_change:
            return
        return change_detail

    def change_trace_with_normal_file(self, f_path):
        file_change = False
        trace_detail = self.file_map[f_path]
        # stamp = os.stat(f_path).st_ctime
        stamp = get_stamp(f_path)
        change_lines = get_change_lines(trace_detail, stamp)
        if self.changed(f_path, stamp):
            file_change = True

        change_details = ChangDetail(
            stamp=stamp,
            lines=get_line_counts(f_path),
            filename=f_path,
            isdir=get_isdir(f_path),
            change_lines=change_lines,
            is_change=file_change
        )
        self.file_map[f_path] = change_details
        if not file_change:
            return
        return change_details

    def change_trace_with_delete_file(self, f_path):
        change_detail = self.file_map.pop(f_path)
        change_detail = ChangDetail(
            stamp=-1,
            lines=0,
            filename=change_detail.filename,
            isdir=get_isdir(change_detail.filename),
            change_lines=-change_detail.lines,
            is_change=True
        )
        return change_detail

    def change_trace(self):
        change_details = []
        pre_file_set = set(self.file_map.keys())
        cur_file_set = set(f for f in recursion_file(self.filepath, self.excludes))
        new_file_set = tuple(cur_file_set - pre_file_set)
        reduce_file_set = tuple(pre_file_set - cur_file_set)
        common_file_set = tuple(cur_file_set & pre_file_set)

        handle_change_trace_map = {
            new_file_set: self.change_trace_with_new_file,
            reduce_file_set: self.change_trace_with_delete_file,
            common_file_set: self.change_trace_with_normal_file
        }

        for file_set, handle_func in handle_change_trace_map.items():
            for f_path in file_set:
                change_detail = handle_func(f_path)
                if change_detail is not None:
                    change_details.append(change_detail)

        if change_details:
            self.is_change = True

        return change_details

    def get_output_time(self):
        if self.test == True:
            return 'TEST TIME 2000年1月1日 1点1分1秒'
        return datetime.datetime.now().strftime('%H:%M:%S')

    def load_description_head(self, **kwargs):
        output = kwargs.get('output')
        status = kwargs.get('status')
        output_time = kwargs.get('output_time')
        cmd = kwargs.get('cmd')
        self.output(u'项目名称 %s' % self.project)
        # self.output(u'目录：%s ' % self.filepath)
        self.output(u'执行时间 🕒 %s' % output_time)
        self.output(u'执行命令 🚀 %s' % cmd)
        status = u'😃' if not status else u'😡'
        self.output(u'执行结果 %s %s' % (status, output))
        # self.output(u'执行输出：%s ' % output)
        self.output(u'文件变更 📝')

    def exec_command(self, cmd):
        output_time = self.get_output_time()
        status, output = commands.getstatusoutput(cmd)
        self.load_description_head(status=status, output=output, output_time=output_time, cmd=cmd)

    def reload_once(self, cmd):
        self.is_change = False
        change_details = self.change_trace()
        if self.is_change:
            self.exec_command(cmd)
            self.gen_change_print(change_details)

    def auto_reload(self, cmd):
        while True:
            self.reload_once(cmd)
            yield


#
if __name__ == '__main__':
    cmd = 'echo'
    watcher = Watcher('a')
    watcher.auto_reload(cmd)
