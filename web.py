#!/usr/bin/env python
# -*- coding: utf-8 -*-

import stock

from flask import Flask
from flask import render_template


app = Flask(__name__)


@app.route('/')
def index():
	date_list = stock.get_qfii_list()
	qfii_data = stock.get_qfii_data()
	qfii_list = []
	if len(date_list) > 0:
		qfii_list = qfii_data[date_list[0]]
	return render_template('index.html', result_num=len(qfii_list), qfii_list=qfii_list)


@app.route('/demo')
def demo():
	return render_template('demo.html')


if __name__ == '__main__':
    app.run(debug=True)
