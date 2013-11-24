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
	if len(stock.categories) > 0:
		category = stock.categories[0]
		if category in stock.holding_date_cache and len(stock.holding_date_cache[category]) > 0:
			holding_dates = stock.holding_date_cache[category]
			holding_date = stock.holding_date_cache[category][0]
			holding_list = stock.get_holding_data(category, holding_date)
	return render_template(
		'index.html',
		category_names=stock.category_names,
		category=category,
		holding_date=holding_date,
		holding_dates=holding_dates,
		a='',
		d='',
		holding_list=holding_list,
		)


@app.route('/holding/<category>/<holding_date>')
def holdings(category='', holding_date=''):
	a, d = parse_request('a', 'd')
	holding_dates = stock.holding_date_cache[category]
	holding_list = stock.get_holding_data(category, holding_date, a, d)
	return render_template(
		'index.html',
		category=category,
		category_names=stock.category_names,
		holding_dates=holding_dates,
		holding_date=holding_date,
		a=a,
		d=d,
		holding_list=holding_list,
		)


@app.route('/trend/<code>/<name>')
def trend(code='', name=''):
	return render_template('stock.html', code=code, name=name, season_increase=stock.get_season_increase(code))


@app.route('/current/<code>')
def get_current_data(code):
	return jsonify(current=stock.get_current_data(code))


@app.route('/history/<code>')
def history(code=''):
	return jsonify(history=stock.get_history_data(code))


@app.route('/advance')
def advance():
	holding_dates = stock.get_holding_dates()
	holding_date = holding_dates[0]
	return render_template(
		'advance.html',
		holding_dates=holding_dates,
		holding_date=holding_date,
		ja='',
		jd='',
		sa='',
		sd='',
		qa='',
		qd='',
		cross_ret=stock.cross_select(holding_date),
		)


@app.route('/advance/<holding_date>')
def advance_sieve(holding_date=''):
	holding_dates = stock.get_holding_dates()
	ja, jd, sa, sd, qa, qd = parse_request('ja', 'jd', 'sa', 'sd', 'qa', 'qd')
	return render_template(
		'advance.html',
		holding_dates=holding_dates,
		holding_date=holding_date,
		ja=ja,
		jd=jd,
		sa=sa,
		sd=sd,
		qa=qa,
		qd=qd,
		cross_ret=stock.cross_select(holding_date, ja, jd, sa, sd, qa, qd),
		)


def parse_request(*params):
	ret = []
	for p in params:
		v = request.args.get(p)
		ret.append(v if v is not None else '')
	return ret


if __name__ == '__main__':
	stock.load_holding_data()
	app.run(debug=True)
