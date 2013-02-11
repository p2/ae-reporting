# good morning!

import bottle
import json

import rule


application = bottle.Bottle()


@application.route('/')
def index():
	try:
		return bottle.static_file('index.html', root='static')
	except Exception, e:
		return 'Not possible: %s' % e


@application.route('/authorize')
def authorize():
	try:
		return bottle.static_file('authorize.html', root='static')
	except Exception, e:
		return 'Not possible: %s' % e


@application.route('/rules/')
def rules():
	return json.dumps(rule.Rule.load_rules(), cls=rule.JSONRuleEncoder)
		
