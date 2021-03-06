#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import time
import urllib2
import datetime

from bs4 import BeautifulSoup


categories = ('jjzc', 'qfii', 'sbzc')
category_names = { 'jjzc' : u'基金重仓', 'qfii' : u'QFII重仓', 'sbzc' : u'社保重仓' }

holding_date_cache = { 'jjzc' : [], 'qfii' : [], 'sbzc' : [] }
holding_data_cache = { 'jjzc' : {}, 'qfii' : {}, 'sbzc' : {} }


def load_holding_data():
    global categories
    global holding_date_cache
    global holding_data_cache
    for category in categories:
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


def get_holding_dates(category='all'):
    global holding_date_cache
    if category in holding_date_cache:
        return holding_date_cache[category]
    elif category == 'all':
        dates = []
        for key in holding_date_cache:
            dates += holding_date_cache[key]
        holding_dates = list(set(dates))
        holding_dates.sort(reverse=True)
        return holding_dates
    else:
        return []


def get_holding_data(category, holding_date, a='', d=''):

    def to_float(*num):
        ret = []
        for n in num:
            try:
                n = float(n)
            except Exception, e:
                n = ''
                print e
            ret.append(n)
        return ret
    
    global holding_data_cache
    if category in holding_data_cache and holding_date in holding_data_cache[category]:
        a, d = to_float(a, d)
        holding_list = holding_data_cache[category][holding_date]
        if a is not '':
            holding_list = [holding for holding in holding_list if holding.a_percent >= a]
        if d is not '':
            holding_list = [holding for holding in holding_list if holding.delta_num_percent == u'新进' or float(holding.delta_num_percent) >= d]
        return holding_list
    else:
        return []


def get_current_data(code):
    current_data = []
    if len(code) == 6:
        url = 'http://hq.sinajs.cn/list=' + ('sh' + code) if int(code[0]) >= 6 else ('sz' + code)
        try:
            response = urllib2.urlopen(url, timeout=3).read().decode('GB2312')
            soup = BeautifulSoup(response)
            matches = re.findall(r'\"(.+?)\"', soup.string)
            current_data = ','.join(matches).split(',')
        except Exception, e:
            print e
    return current_data


def get_season_data(code):
    season_data = []
    history_path = './data/history/' + code
    if os.path.isfile(history_path):
        with open(history_path) as history_file:
            lines = [line for line in history_file]
            pre_month = -1
            for line in lines[1:]:
                data = line.split(',')
                try:
                    data[0] = datetime.datetime.strptime(data[0], '%Y-%m-%d')
                    if data[0].month in (12, 9, 6, 3) and data[0].month is not pre_month:
                        for i in range(1, len(data), 1):
                            data[i] = float(data[i])
                        season_data.append(data)
                        pre_month = data[0].month
                except Exception, e:
                    print e
    return season_data


def get_season_increase(code):
    
    def get_season(input_datetime):
        if isinstance(input_datetime, datetime.datetime):
            if input_datetime.month in (1, 2, 3):
                return str(input_datetime.year) + '-1'
            elif input_datetime.month in (4, 5, 6):
                return str(input_datetime.year) + '-2'
            elif input_datetime.month in (7, 8, 9):
                return str(input_datetime.year) + '-3'
            elif input_datetime.month in (10, 11, 12):
                return str(input_datetime.year) + '-4'
        else:
            return input_datetime
    
    season_increase = []
    season_data = get_season_data(code)
    for i in range(len(season_data)):
        data = season_data[i]
        season = get_season(data[0])
        increase = '0'
        if i < len(season_data) - 1:
            next_data = season_data[i + 1]
            adj_close_index = 6
            if next_data[adj_close_index] > 0:
                increase = ('%+.2f' % (100 * (data[adj_close_index] - next_data[adj_close_index]) / next_data[adj_close_index]))
            else:
                if data[adj_close_index] > 0:
                    increase = '+∞'
                elif data[adj_close_index] == 0:
                    increase = '0'
                elif data[adj_close_index] < 0:
                    increase = '-∞'
        else:
            increase = 'none'
        season_increase.append((season, data[adj_close_index], increase))
    return season_increase


def get_history_data(code):
    history_data = []
    history_path = './data/history/' + code
    if os.path.isfile(history_path):
        with open(history_path) as history_file:
            lines = [line for line in history_file]
            for line in lines[1:]:
                data = line.strip().split(',')
                try:
                    data[0] = time.mktime(datetime.datetime.strptime(data[0], '%Y-%m-%d').timetuple()) * 1000
                    for i in range(1, len(data), 1):
                        data[i] = float(data[i])
                    history_data.append(data)
                except Exception, e:
                    print e
    history_data.reverse()
    return history_data


def cross_select(holding_date, jj=1, sb=1, qf=1, ja='', jd='', sa='', sd='', qa='', qd=''):
    cross_ret = {}
    condition = { 'jjzc' : [jj, ja, jd], 'sbzc' : [sb, sa, sd], 'qfii' : [qf, qa, qd] }
    for category in categories:
        if condition[category][0] == 1:
            for holding in get_holding_data(category, holding_date, condition[category][1], condition[category][2]):
                if holding.code not in cross_ret:
                    cross_ret[holding.code] = {}
                cross_ret[holding.code][category] = holding
    cross_ret = dict((key, value) for key, value in cross_ret.iteritems() if len(value) == (jj + sb + qf))
    return cross_ret


class Holding(object):
    
    def __init__(self, line=None):
        fmt_ok = False
        if line is not None:
            parts = line.split(',')
            if len(parts) >= 9:
                try:
                    self._code = parts[0]
                    self._name = parts[1]
                    self._date = parts[2]
                    self._count = float(parts[3])
                    self._stock_num = float(parts[4])
                    self._a_percent = float(parts[5])
                    self._delta_num = float(parts[6])
                    self._percent = float(parts[7])
                    self._pre_count = float(parts[8])
                    pre_stock_num = self.stock_num - self.delta_num
                    if pre_stock_num > 0:
                        self._delta_num_percent = '%.2f' % (100 * self.delta_num / pre_stock_num)
                    else:
                        self._delta_num_percent = u'新进'
                    fmt_ok = True
                except Exception, e:
                    print e
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
            self._delta_num_percent = u'新进'

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

    @property
    def delta_num_percent(self):
        return self._delta_num_percent

    def get_line(self):
        ret = self.code.encode('utf-8')
        ret += ',' + self.name.encode('utf-8')
        ret += ',' + self.date.encode('utf-8')
        ret += ',' + str(self.count)
        ret += ',' + str(self.stock_num)
        ret += ',' + str(self.a_percent)
        ret += ',' + str(self.delta_num)
        ret += ',' + str(self.percent)
        ret += ',' + str(self.pre_count)
        return ret

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
