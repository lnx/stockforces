#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import time
import json
import stock
import flask
import urllib2
import datetime

from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template

from bs4 import BeautifulSoup


app = Flask(__name__)


@app.route('/')
def index():
	holding_list = []
	if len(stock.categories):
		category = stock.categories[0]
		category_names = stock.category_names
		if category in stock.holding_date_cache and len(stock.holding_date_cache[category]) > 0:
			holding_date = stock.holding_date_cache[category][0]
			holding_date_list = stock.holding_date_cache[category]
			holding_list = stock.get_holding_data(category, holding_date)
	return render_template('index.html', a='', d='', category=category, category_names=category_names, holding_date=holding_date, holding_date_list=holding_date_list, result_num=len(holding_list), holding_list=holding_list)


@app.route('/<category>/<holding_date>', methods=['GET', 'POST'])
def holdings(category='', holding_date=''):
	a = ''
	d = ''
	if request.method == 'GET':
		try:
			a = float(request.args.get('a'))
		except Exception, e:
			pass
		try:
			d = float(request.args.get('d'))
		except Exception, e:
			pass
	elif request.method == "POST":
		try:
			a = float(request.form['a'])
		except Exception, e:
			pass
		try:
			d = float(request.form['d'])
		except Exception, e:
			pass
	category_names = stock.category_names
	holding_date_list = stock.holding_date_cache[category]
	holding_list = stock.get_holding_data(category, holding_date)
	if a is not '':
		holding_list = [holding for holding in holding_list if holding.a_percent >= a]
	if d is not '':
		holding_list = [holding for holding in holding_list if holding.delta_num >= d]
	return render_template('index.html', a=a, d=d, category=category, category_names=category_names, holding_date=holding_date, holding_date_list=holding_date_list, result_num=len(holding_list), holding_list=holding_list)


@app.route('/trend/<code>/<name>')
def chart(code='', name=''):
	return render_template('stock.html', code=code, name=name)


@app.route('/history/<code>')
def history(code=''):
	history_data = []
	history_path = './data/history/' + code
	if os.path.isfile(history_path):
		with open(history_path) as history_file:
			lines = [line for line in history_file]
			for line in lines[1:]:
				data = line.split(',')
				try:
					data[0] = time.mktime(datetime.datetime.strptime(data[0], '%Y-%m-%d').timetuple()) * 1000
					for i in range(1, len(data), 1):
						data[i] = float(data[i])
					history_data.append(data)
				except Exception, e:
					pass
	history_data.reverse()
	return jsonify(history=history_data)


@app.route('/current/<code>')
def get_current_data(code):
	current_data = []
	if len(code) == 6:
		url = 'http://hq.sinajs.cn/list=' + ('sh' + code) if int(code[0]) >= 6 else ('sz' + code)
		try:
			response = urllib2.urlopen(url, timeout=3).read().decode('GB2312')
			soup = BeautifulSoup(response)
			matches = re.findall(r'\"(.+?)\"',soup.string)
			current_data = ','.join(matches).split(',')
		except Exception, e:
			pass
	return jsonify(current=current_data)


if __name__ == '__main__':
	for category in stock.categories:
		stock.load_holding_data(category)
	app.run(debug=True)
