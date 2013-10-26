#!/usr/bin/env python

import os
import urllib


def download_history_data(code):
    url = 'http://table.finance.yahoo.com/table.csv?s='
    if len(code) == 6:
        if int(code[0]) >= 6:
            url += code + '.ss'
        else:
            url += code + '.sz'
        print url


if __name__ == '__main__':
    # print len(get_qfii_codes())
    url = 'http://table.finance.yahoo.com/table.csv?s=002024.szss'
    urllib.urlretrieve(url, 'table.csv')
