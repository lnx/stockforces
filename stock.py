#!/usr/bin/env python

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
                parts = line.split(' ')
                data = QFII()
                data.code = parts[0]
                data.name = parts[1]
                data.date = parts[2]
                data.count = parts[3]
                data.stock_num = parts[4]
                data.a_percent = parts[5]
                data.delta_num = parts[6]
                data.percent = parts[7]
                data.pre_count = parts[8]
                qfii_codes.add(data.code)
                qfii_data[qfii].append(data)
    qfii_codes = list(qfii_codes)
    qfii_codes.sort()
    qfii_last_udpate = os.stat(qfii_dir).st_mtime
    print 'read qfii data ' + str(datetime.now())


class QFII():
    
    code = ''
    name = ''
    date = ''
    count = 0
    stock_num = 0
    a_percent = 0
    delta_num = 0
    percent = 0
    pre_count = 0
    
    def __str__(self):
        ret = ''
        ret += '(code=' + self.code
        ret += ',name=' + self.name
        ret += ',date=' + self.date
        ret += ',count=' + str(self.count)
        ret += ',stock_num=' + str(self.stock_num)
        ret += ',a_percent=' + str(self.a_percent)
        ret += ',delta_num=' + str(self.delta_num)
        ret += ',percent=' + str(self.percent)
        ret += ',pre_count=' + str(self.pre_count) + ')'
        return ret

    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':
    print get_qfii_list()
