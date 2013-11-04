#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import urllib
import urllib2
import threading

from bs4 import BeautifulSoup


def update_history_data():
    def read_codes(file_path, codes):
        with open(file_path) as f:
            for line in f.readlines():
                codes.append(line.split(' ')[0])
    codes = []
    read_codes('./data/code/sh', codes)
    read_codes('./data/code/sz', codes)
    for code in codes:
        download_history_data(code)
    history_list = [history for history in os.listdir('./data/history') if history in codes]
    print 'Update history data %s!\n' % 'success' if len(codes) == len(history_list) else 'failure',


def download_history_data(code):
    
    def download(code):
        file_path = './data/history/' + code + '.tmp'
        urllib.urlretrieve(url, file_path)
        success = False
        with open(file_path) as history:
            lines = history.readlines()
            if len(lines) > 0:
                if lines[0].strip() == 'Date,Open,High,Low,Close,Volume,Adj Close':
                    success = True
                    os.rename(file_path, './data/history/' + code)
            if not success:
                os.remove(file_path)
        return success
    
    success = False
    if len(code) == 6:
        url = 'http://table.finance.yahoo.com/table.csv?s='
        if int(code[0]) >= 6:
            url += code + '.ss'
        else:
            url += code + '.sz'
        print 'downloading %s' % url,
        sys.stdout.flush()
        success = download(code)
        print 'success\n' if success else 'failure\n',
    return success


def update_holding_data():
    waiting_list = []
    categories = ['jjzc', 'sbzc', 'qfii']
    date_quarter_dict = { '2013' : [3, 2, 1], '2012' : [4, 3, 2, 1], '2011' : [4, 3, 2, 1], '2010' : [4, 3, 2, 1], '2009' : [4, 3, 2, 1] }
    dates = date_quarter_dict.keys()
    dates.sort(reverse=True)
    for category in categories:
        for date in dates:
            for quarter in date_quarter_dict[date]:
                waiting_list.append((category, date, quarter))
    while True:
        workers = []
        failure_list = []
        for param in waiting_list:
            tid = param[0] + '_' + param[1] + '_' + str(param[2])
            params = (failure_list, param[0], param[1], param[2])
            workers.append(Worker(tid, download_holding_data, params))
        for worker in workers:
            worker.start()
        for worker in workers:
           worker.join()
        if len(failure_list) > 0:
            waiting_list = failure_list
        else:
            break
    print 'Update holding data success!\n',


def download_holding_data(failure_list, category, date, quarter, page=1):
    holding_data_list = []
    url = 'http://vip.stock.finance.sina.com.cn/q/go.php/vComStockHold/kind/' + category + '/index.phtml?reportdate=' + date + '&quarter=' + str(quarter) + '&p=' + str(page)
    print 'downloading %s\n' % url,
    try:
        html = urllib2.urlopen(url).read().decode('GB2312')
        soup = BeautifulSoup(html)
        table = soup.find(id='dataTable')
        for tr in table.find_all('tr', recursive=False):
            if not tr.has_attr('style'):
                holding_data = [td.string for td in tr.find_all('td', recursive=False)[:9]]
                holding_data_list.append(holding_data)
        if len(holding_data_list) > 0 and soup.find('div', class_='pages').find('a', class_='page nolink', text=u'下一页') is None:
            holding_data_list += download_holding_data(failure_list, category, date, quarter, page + 1)
        if page == 1:
            with open('./data/' + category + '/' + date + '_' + str(quarter), 'w') as f:
                for holding_data in holding_data_list:
                    f.write(','.join(holding_data).encode('utf-8') + '\n')
    except:
        print 'downloading %s failure -> add (%s, %s, %d) to failure_list\n' % (url, category, date, quarter),
        failure_list.append((category, date, quarter))
    return holding_data_list


def check_holding_data():
    categories = ['jjzc', 'sbzc', 'qfii']
    date_quarter_dict = { '2013' : [3, 2, 1], '2012' : [4, 3, 2, 1], '2011' : [4, 3, 2, 1], '2010' : [4, 3, 2, 1], '2009' : [4, 3, 2, 1] }
    dates = date_quarter_dict.keys()
    dates.sort(reverse=True)
    all_data_ok = True
    for category in categories:
        for date in dates:
            for quarter in date_quarter_dict[date]:
                file_path = './data/' + category + '/' + date + '_' + str(quarter)
                with open(file_path) as f:
                    total = len(f.readlines())
                    page = int(math.ceil(total / 40.0))
                    url = 'http://vip.stock.finance.sina.com.cn/q/go.php/vComStockHold/kind/' + category + '/index.phtml?reportdate=' + date + '&quarter=' + str(quarter) + '&p=' + str(page)
                    html = urllib2.urlopen(url).read().decode('GB2312')
                    soup = BeautifulSoup(html)
                    check_ok = False
                    if soup.find('div', class_='pages').find('a', class_='page nolink', text=u'下一页') is not None:
                        check_ok = True
                    else:
                        all_data_ok = False
                    print 'checking %s %d %d %s\n' % (file_path, total, page, 'success' if check_ok else 'failure'),
    print 'The data is %s\n' % 'complete' if all_data_ok else 'not complete',


class Worker(threading.Thread):

    def __init__(self, tid, work, params):
        threading.Thread.__init__(self)
        self.tid = tid
        self.work = work
        self.params = params

    def run(self):
        self.work(*self.params)


if __name__ == '__main__':
    update_history_data()
