#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib

from datetime import datetime


qfii_dir = './data/qfii/'
qfii_last_udpate = 0

qfii_list  = [] # example: ['2013_3', '2012_1', '2010_2']
qfii_codes = [] # stock codes in qfii_data
qfii_data  = {} # load all of the local data


def get_qfii_list():
    if need_update():
        read_qfii_data()
    return qfii_list


def get_qfii_codes():
    if need_update():
        read_qfii_data()
    return qfii_codes


def get_qfii_data():
    if need_update():
        read_qfii_data()
    return qfii_data


def need_update():
    update = False
    global qfii_dir
    global qfii_last_udpate
    latest = os.stat(qfii_dir).st_mtime
    if latest > qfii_last_udpate:
        update = True
    return update


def read_qfii_data():
    global qfii_dir
    global qfii_last_udpate
    global qfii_list
    global qfii_codes
    qfii_list = [qfii for qfii in os.listdir(qfii_dir) if os.path.isfile(qfii_dir + qfii)]
    qfii_list.sort(reverse=True)
    qfii_codes = set([])
    for qfii in qfii_list:
        qfii_data[qfii] = []
        with open(qfii_dir + qfii) as qfii_file:
            for line in qfii_file:
                data = Holding(line.decode('utf-8').strip())
                qfii_codes.add(data.code)
                qfii_data[qfii].append(data)
    qfii_codes = list(qfii_codes)
    qfii_codes.sort()
    qfii_last_udpate = os.path.getmtime(qfii_dir)
    print 'read qfii data ' + str(datetime.now())


class Holding(object):
    
    def __init__(self, line=None):
        fmt_ok = False
        if line is not None:
            parts = line.split(' ')
            if len(parts) >= 9:
                self._code = parts[0]
                self._name = parts[1]
                self._date = parts[2]
                self._count = float(parts[3])
                self._stock_num = float(parts[4])
                self._a_percent = float(parts[5])
                self._delta_num = float(parts[6])
                self._percent = float(parts[7])
                self._pre_count = float(parts[8])
                fmt_ok = True
        if fmt_ok is False:
            self._code = u''
            self._name = u''
            self._date = u''
            self._count = 0.0
            self._stock_num = 0.0
            self._a_percent = 0.0
            self._delta_num = 0.0
            self._percent = 0.0
            self._pre_count = 0.0

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name

    @property
    def date(self):
        return self._date

    @property
    def count(self):
        return self._count

    @property
    def stock_num(self):
        return self._stock_num

    @property
    def a_percent(self):
        return self._a_percent

    @property
    def delta_num(self):
        return self._delta_num

    @property
    def percent(self):
        return self._percent

    @property
    def pre_count(self):
        return self._pre_count

    def __str__(self):
        ret = ''
        ret += '(code=' + self.code.encode('utf-8')
        ret += ',name=' + self.name.encode('utf-8')
        ret += ',date=' + self.date.encode('utf-8')
        ret += ',count=' + str(self.count)
        ret += ',stock_num=' + str(self.stock_num)
        ret += ',a_percent=' + str(self.a_percent)
        ret += ',delta_num=' + str(self.delta_num)
        ret += ',percent=' + str(self.percent)
        ret += ',pre_count=' + str(self.pre_count) + ')'
        return ret

    def __repr__(self):
        return self.__str__()


def History(Object):
    pass


if __name__ == '__main__':
    print get_qfii_data()
