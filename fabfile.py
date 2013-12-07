#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import *

env.roledefs = { 'nlsde' : ['grid@nlsde',] }

@roles('nlsde')
def deploy():
    put('~/project/stockforces/*.py', '~/stockforces/')
    put('~/project/stockforces/templates', './stockforces/')
    put('~/project/stockforces/static/stylesheets/*', './stockforces/static/stylesheets/')
    run('sed -i "s/app.run()/app.run(host=\'218.241.236.69\')/g" ~/stockforces/web.py')
