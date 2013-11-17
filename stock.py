#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib
import datetime


categories = ('jjzc', 'qfii', 'sbzc')
category_names = { 'jjzc' : u'基金重仓', 'qfii' : u'QFII重仓', 'sbzc' : u'社保重仓' }

holding_date_cache = { 'jjzc' : [], 'qfii' : [], 'sbzc' : [] }
holding_data_cache = { 'jjzc' : {}, 'qfii' : {}, 'sbzc' : {} }


def get_holding_dates(category):
    global holding_date_cache
    if category in holding_date_cache:
        return holding_date_cache[category]
    else:
        return []


def get_holding_data(category, holding_date):
    global holding_data_cache
    if category in holding_data_cache and holding_date in holding_data_cache[category]:
        return holding_data_cache[category][holding_date]
    else:
        return []


def load_holding_data(category):
    global categories
    global holding_date_cache
    global holding_data_cache
    if category in categories:
        if category not in holding_date_cache:
            holding_date_cache[category] = []
        if category not in holding_data_cache:
            holding_data_cache[category] = {}
        holding_dir = './data/' + category
        if os.path.isdir(holding_dir):
            holding_date_cache[category] = [holding_date for holding_date in os.listdir(holding_dir) if os.path.isfile(holding_dir + '/' + holding_date)]
            holding_date_cache[category].sort(reverse=True)
            for holding_date in holding_date_cache[category]:
                holding_data_cache[category][holding_date] = []
                with open(holding_dir + '/' + holding_date) as holding_file:
                    for line in holding_file:
                        holding_data_cache[category][holding_date].append(Holding(line.decode('utf-8').strip()))
        print 'load %s data at %s\n' % (category, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    else:
        print '%s is not a valid category\n' % category,


class Holding(object):
    
    def __init__(self, line=None):
        fmt_ok = False
        if line is not None:
            parts = line.split(',')
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
