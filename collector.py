#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import time
import urllib
import urllib2
import datetime
import threading

from bs4 import BeautifulSoup


def update_history_data(thread_num=30):
    
    def read_codes(fp, codes):
        with open(fp) as f:
            for line in f.readlines():
                codes.append(line.split(' ')[0])

    codes = []
    read_codes('./data/code/sh', codes)
    read_codes('./data/code/sz', codes)
    
    codes_need_update = [code for code in codes]
    for history in os.listdir('./data/history'):
        if history in codes and datetime.date.today() == datetime.date.fromtimestamp(os.path.getmtime('./data/history/' + history)):
            codes_need_update.remove(history)
    print 'all=%d need_to_update=%d\n' % (len(codes), len(codes_need_update)),

    workers = []
    for i in range(0, thread_num):
        wcodes = []
        for j in range(i, len(codes_need_update), thread_num):
            wcodes.append(codes_need_update[j])
        worker = Worker(str(i), download_history_data, (wcodes,))
        worker.start()
        workers.append(worker)
    for worker in workers:
       worker.join()

    history_list = []
    for history in os.listdir('./data/history'):
        if history in codes:
            if datetime.date.today() == datetime.date.fromtimestamp(os.path.getmtime('./data/history/' + history)):
                history_list.append(history)
        else:
            os.remove('./data/history/' + history)
    print '%s %.2f%% is updated!\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), (100 * len(history_list) / float(len(codes)))), 


def download_history_data(codes):
    
    def download(url, code):
        fp = './data/history/' + code
        success = False
        try:
            csv_data = urllib2.urlopen(url, timeout=10).read()
            if csv_data.startswith('Date,Open,High,Low,Close,Volume,Adj Close'):
                with open(fp, 'w') as history:
                    history.write(csv_data)
                success = True
        except Exception as e:
            pass
        return success

    for code in codes:
        if len(code) == 6:
            url = 'http://table.finance.yahoo.com/table.csv?s='
            if int(code[0]) >= 6:
                url += code + '.ss'
            else:
                url += code + '.sz'
            print 'downloading %s %s\n' % (url, 'success' if download(url, code) else 'failure'),


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
            worker = Worker(tid, download_holding_data, params)
            worker.start()
            workers.append(worker)
        for worker in workers:
           worker.join()
        if len(failure_list) > 0:
            waiting_list = failure_list
        else:
            break
    print 'Update holding data successfully!\n',


def download_holding_data(failure_list, category, date, quarter, page=1):
    holding_data_list = []
    url = 'http://vip.stock.finance.sina.com.cn/q/go.php/vComStockHold/kind/' + category + '/index.phtml?reportdate=' + date + '&quarter=' + str(quarter) + '&p=' + str(page)
    print 'downloading %s\n' % url,
    try:
        html = urllib2.urlopen(url, timeout=5).read().decode('GB2312')
        soup = BeautifulSoup(html)
        table = soup.find(id='dataTable')
        for tr in table.find_all('tr', recursive=False):
            if not tr.has_attr('style'):
                holding_data = [td.string for td in tr.find_all('td', recursive=False)[:9]]
                holding_data_list.append(holding_data)
        if len(holding_data_list) > 0 and soup.find('div', class_='pages').find('a', class_='page nolink', text=u'下一页') is None:
            holding_data_list += download_holding_data(failure_list, category, date, quarter, page + 1)
        if page == 1 and (category, date, quarter) not in failure_list:
            print 'updating %s_%s_%d size=%d\n' % (category, date, quarter, len(holding_data_list)),
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
                fp = './data/' + category + '/' + date + '_' + str(quarter)
                with open(fp) as f:
                    total = len(f.readlines())
                    page = int(math.ceil(total / 40.0))
                    url = 'http://vip.stock.finance.sina.com.cn/q/go.php/vComStockHold/kind/' + category + '/index.phtml?reportdate=' + date + '&quarter=' + str(quarter) + '&p=' + str(page)
                    html = urllib2.urlopen(url, timeout=5).read().decode('GB2312')
                    soup = BeautifulSoup(html)
                    check_ok = False
                    if soup.find('div', class_='pages').find('a', class_='page nolink', text=u'下一页') is not None:
                        check_ok = True
                    else:
                        all_data_ok = False
                    print 'checking %s %d %d %s\n' % (fp, total, page, 'success' if check_ok else 'failure'),
    print 'The data is %s!\n' % 'complete' if all_data_ok else 'not complete',


class Worker(threading.Thread):

    def __init__(self, tid, work, params):
        threading.Thread.__init__(self)
        self.tid = tid
        self.work = work
        self.params = params

    def run(self):
        self.work(*self.params)


if __name__ == '__main__':
    # update_holding_data()
    # check_holding_data()
    while True:
        for i in range(3):
            update_history_data()
            time.sleep(600)
        time.sleep(28800)
