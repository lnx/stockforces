#!/usr/bin/env python
# -*- coding: utf-8 -*-

import stock

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
	p = ''
	if request.method == 'GET':
		try:
			a = float(request.args.get('a'))
		except Exception, e:
			print e
		try:
			p = float(request.args.get('p'))
		except Exception, e:
			print e
	elif request.method == "POST":
		try:
			a = float(request.form['a'])
		except Exception, e:
			print e
		try:
			p = float(request.form['p'])
		except Exception, e:
			print e
	category_names = stock.category_names
	holding_date_list = stock.holding_date_cache[category]
	holding_list = stock.get_holding_data(category, holding_date)
	if a is not '':
		holding_list = [holding for holding in holding_list if holding.a_percent >= a]
	if p is not '':
		holding_list = [holding for holding in holding_list if holding.percent >= p]
	return render_template('index.html', a=a, p=p, category=category, category_names=category_names, holding_date=holding_date, holding_date_list=holding_date_list, result_num=len(holding_list), holding_list=holding_list)


@app.route('/trend/<code>/<name>')
def trend(code='', name=''):
	return render_template('stock.html', code=code, name=name, season_increase=stock.get_season_increase(code))


@app.route('/current/<code>')
def get_current_data(code):
	return jsonify(current=stock.get_current_data(code))


@app.route('/history/<code>')
def history(code=''):
	return jsonify(history=stock.get_history_data(code))


if __name__ == '__main__':
	for category in stock.categories:
		stock.load_holding_data(category)
	app.run(debug=True)
