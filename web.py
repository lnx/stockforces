#!/usr/bin/env python
# -*- coding: utf-8 -*-

import stock

from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask import Response

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
		category_names=stock.category_names,
		holding_dates=holding_dates,
		holding_date=holding_date,
		jj=1,
		sb=1,
		qf=1,
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
	jj, sb, qf, ja, jd, sa, sd, qa, qd = parse_request('jj', 'sb', 'qf', 'ja', 'jd', 'sa', 'sd', 'qa', 'qd')
	jj, sb, qf = parse_checkbox(jj, sb, qf)
	return render_template(
		'advance.html',
		category_names=stock.category_names,
		holding_dates=holding_dates,
		holding_date=holding_date,
		jj=jj,
		sb=sb,
		qf=qf,
		ja=ja,
		jd=jd,
		sa=sa,
		sd=sd,
		qa=qa,
		qd=qd,
		cross_ret=stock.cross_select(holding_date, jj, sb, qf, ja, jd, sa, sd, qa, qd),
		)


@app.route('/download/<download_type>')
def download(download_type=''):

	def generate(holding_list):
		for holding in holding_list:
			yield holding.get_line() + '\n'
	
	holding_list = []
	if download_type == 'single':
		holding_list = stock.get_holding_data(*parse_request('category', 'holding_date', 'a', 'd'))
	elif download_type == 'multiple':
		params = parse_request('holding_date', 'jj', 'sb', 'qf', 'ja', 'jd', 'sa', 'sd', 'qa', 'qd')
		params = params[:1] + parse_checkbox(*params[1:4]) + params[4:]
		cross_ret = stock.cross_select(*params)
		for code in cross_ret:
			for category in cross_ret[code]:
				holding_list.append(cross_ret[code][category])
	response = Response(generate(holding_list), mimetype='text/csv')
	response.headers['Content-Disposition'] = 'attachment; filename=stockforces.csv'
	return response


def parse_request(*params):
	ret = []
	for p in params:
		v = request.args.get(p)
		ret.append(v if v is not None else '')
	return ret


def parse_checkbox(*params):
    ret = []
    for p in params:
        v = 1 if p == 'on' or p == '1' else 0
        ret.append(v)
    return ret


if __name__ == '__main__':
	stock.load_holding_data()
	app.run()
