# good morning!

import bottle
import json
from jinja2 import Template
from jinja2 import Environment, PackageLoader

import rule
from tokenstore import TokenStore
from smart_client_python.client import SMARTClient

from settings import APP_ID, API_BASE, OAUTH_PARAMS


# bottle and Jinja setup
app = bottle.Bottle()
env = Environment(loader=PackageLoader('action', 'templates'), trim_blocks=True)
_smart = None
DEBUG = True


def _serve_static(file, root):
	""" Serves a static file or a 404 """
	try:
		return bottle.static_file(file, root=root)
	except Exception, e:
		bottle.abort(404)


def _smart_client(record_id=None):
	global _smart
	if _smart is None:
		_smart = SMARTClient(APP_ID, API_BASE, OAUTH_PARAMS)
		_smart.record_id = record_id
	return _smart

def _log_debug(log):
	if DEBUG:
		print log

def _log_error(err):
	print err
		


# ------------------------------------------------------------------------------ Token Handling
def _test_record_token(record_id, token):
	""" Tries to fetch demographics with the given token and returns a bool whether thas was successful """
	
	smart = _smart_client(record_id)
	smart.update_token(token)
	try:
		demo = smart.get_demographics()
		if '200' == demo.response.get('status'):
			return True
	except Exception, e:
		pass
	
	return False


def _request_token_for_record_if_needed(record_id):
	""" Requests a request token for record id, if needed """
	ts = TokenStore(API_BASE)
	token = ts.tokenForRecord(record_id)
	
	# we already got a token, test if it still works
	if token is not None and _test_record_token(record_id, token):
		return False
	
	# request a token
	_log_debug("requesting token for record %s" % record_id)
	smart = _smart_client(record_id)
	smart.token = None
	token = smart.fetch_request_token()
	if token is not None:
		ts = TokenStore(API_BASE)
		if not ts.storeTokenForRecord(record_id, token):
			return False
	
	# now go and authorize the token
	bottle.redirect(smart.auth_redirect_url)
	return True


def _exchange_token(req_token, verifier):
	""" Takes the request token and the verifier, obtained in our authorize callback, and exchanges it for an access
	token. Stores the access token and returns it. """
	ts = TokenStore(API_BASE)
	full_token, record_id = ts.tokenAndRecordForToken(req_token)
	if record_id is None:
		_log_error("Unknown token, cannot exchange %s" % req_token)
		return None
	
	# exchange the token
	_log_debug("exchange token: %s" % full_token)
	smart = _smart_client(record_id)
	smart.update_token(full_token)
	try:
		acc_token = smart.exchange_token(verifier)
	except Exception, e:
		_log_error("token exchange failed: %s" % e)
		return None
	
	# success, store it
	_log_debug("did exchange token: %s" % acc_token)
	ts.storeTokenForRecord(record_id, acc_token)
	smart.update_token(acc_token)
	
	return record_id


# ------------------------------------------------------------------------------ Index
@app.get('/')
@app.get('/index.html')
def index():
	""" The index page makes sure we have a token """
	record_id = bottle.request.query.get('record_id')
	
	# do we have a token?
	if record_id:
		if _request_token_for_record_if_needed(record_id):
			return		# the call above will redirect if true anyway, but let's be sure to exit here
	
	# render index
	template = env.get_template('index.html')
	return template.render(record_id=record_id)


# ------------------------------------------------------------------------------ Authorization
@app.get('/authorize')
def authorize():
	""" Extract the oauth_verifier and exchange it for an access token """
	req_token = {'oauth_token': bottle.request.query.get('oauth_token')}
	verifier = bottle.request.query.get('oauth_verifier')
	record_id = _exchange_token(req_token, verifier)
	if record_id is not None:
		bottle.redirect('/index.html?record_id=%s' % record_id)
	
	# just default to showing the authorize page if we're still here
	return _serve_static('authorize.html', 'static')


# ------------------------------------------------------------------------------ RESTful paths
@app.get('/rules/')
def rules(rule_id=None):
	return json.dumps(rule.Rule.load_rules(), cls=rule.JSONRuleEncoder)

@app.get('/rules/<rule_id>/run_against/<record_id>')
def run_rule(rule_id, record_id):
	""" This runs the given rule against the given record """
	my_rule = rule.Rule.rule_named(rule_id)
	if my_rule is None:
		bottle.abort(404)
	
	# make sure we have the tokens
	
	
	return my_rule.description


# ------------------------------------------------------------------------------ Static requests
@app.get('/static/<filename>')
def static(filename):
	return _serve_static(filename, 'static')

@app.get('/templates/<ejs_name>.ejs')
def ejs(ejs_name):
	return _serve_static('%s.ejs' % ejs_name, 'templates')
