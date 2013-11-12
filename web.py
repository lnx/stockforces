#!/usr/bin/env python
# -*- coding: utf-8 -*-

import stock

from flask import Flask
from flask import render_template


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
	return render_template('index.html', category=category, category_names=category_names, holding_date=holding_date, holding_date_list=holding_date_list, result_num=len(holding_list), holding_list=holding_list)


@app.route('/<category>/<holding_date>')
def holdings(category='', holding_date=''):
	category_names = stock.category_names
	holding_date_list = stock.holding_date_cache[category]
	holding_list = stock.get_holding_data(category, holding_date)
	return render_template('index.html', category=category, category_names=category_names, holding_date=holding_date, holding_date_list=holding_date_list, result_num=len(holding_list), holding_list=holding_list)


@app.route('/demo')
def demo():
	return render_template('demo.html')


if __name__ == '__main__':
	for category in stock.categories:
		stock.load_holding_data(category)
	app.run(debug=True)
