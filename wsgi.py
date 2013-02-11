# good morning!

import bottle
import json

import rule


application = bottle.Bottle()


def serve_static(file, root):
	try:
		return bottle.static_file(file, root=root)
	except Exception, e:
		bottle.abort(404)


@application.route('/')
def index():
	return serve_static('index.html', 'static')


# ------------------------------------------------------------------------------ Authorization
@application.route('/authorize')
def authorize():
	return serve_static('authorize.html', 'static')


# ------------------------------------------------------------------------------ RESTful paths
@application.route('/rules/')
@application.route('/rules/<rule_id>/run')
def rules(rule_id=None):
	if rule_id is None:
		return json.dumps(rule.Rule.load_rules(), cls=rule.JSONRuleEncoder)
	
	# run a specific rule
	my_rule = rule.Rule.rule_named(rule_id)
	if my_rule is None:
		bottle.abort(404)
	
	# working here
	return my_rule.description


# ------------------------------------------------------------------------------ Static requests
@application.route('/css/<filename>')
def css(filename):
	return serve_static(filename, 'css')

@application.route('/js/<filename>')
def js(filename):
	return serve_static(filename, 'js')

@application.route('/templates/<filename>')
def templates(filename):
	return serve_static(filename, 'templates')
