# good morning!

import bottle
import json
from jinja2 import Template, Environment, PackageLoader

from tokenstore import TokenStore
from smart_client_python.client import SMARTClient
from testrecord import TestRecord
from rule import Rule, JSONRuleEncoder

from settings import ENDPOINTS


# bottle and Jinja setup
app = bottle.Bottle()
application = app				# needed for AppFog			
_jinja = Environment(loader=PackageLoader('wsgi', 'templates'), trim_blocks=True)
_smart = None
_cookie_name = 'wookie'

DEBUG = True


def _log_debug(log):
	if DEBUG:
		print log


def _log_error(err):
	print err


def _serve_static(file, root):
	""" Serves a static file or a 404 """
	try:
		return bottle.static_file(file, root=root)
	except Exception, e:
		bottle.abort(404)


def _smart_client(api_base, record_id=None):
	""" Returns the SMART client, configured accordingly """
	global _smart
	if _smart is None or _smart.api_base != api_base:
		server = None
		for ep in ENDPOINTS:
			if ep.get('url') == api_base:
				server = ep
				break
		
		if server is None:
			_log_error("There is no server with base URI %s" % api_base)
			bottle.abort(404)
			return None
		
		# instantiate; when this fails, most likely the server is down
		app_id = server.get('app_id')
		try:
			_smart = SMARTClient(app_id, api_base, server)
		except Exception, e:
			bottle.abort(503)
			return None
	
	_smart.record_id = record_id
	return _smart



# ------------------------------------------------------------------------------ Token Handling
def _test_record_token(api_base, record_id, token):
	""" Tries to fetch demographics with the given token and returns a bool whether thas was successful """
	
	smart = _smart_client(api_base, record_id)
	if smart is None:
		return False
	
	# update tokens
	smart.update_token(token)
	try:
		demo = smart.get_demographics()
		if '200' == demo.response.get('status'):
			return True
	except Exception, e:
		pass
	
	return False


def _request_token_if_needed(request, record_id, api_base):
	""" Requests a request token for record id, if needed.
	"""
	ts = TokenStore()
	cookie = request.get_cookie(_cookie_name)
	token, ex_api_base, ex_record_id = ts.tokenServerRecordForCookie(cookie)
	
	# we already got a token, test if it still works
	if token is not None \
		and (record_id is None or int(ex_record_id) == int(record_id)) \
		and (api_base is None or unicode(ex_api_base) == unicode(api_base)) \
		and _test_record_token(api_base, record_id, token):
		_log_debug("reusing existing token")
		return False, None
	
	# request a fresh token
	bottle.response.delete_cookie(_cookie_name)
	_log_debug("requesting token for record %s on %s" % (record_id, api_base))
	smart = _smart_client(api_base, record_id)
	if smart is None:
		return False, None
	
	smart.token = None
	try:
		token = smart.fetch_request_token()
	except Exception, e:
		return False, str(e)
	
	# got a token, store it
	if token is not None and not ts.storeTokenForRecord(api_base, record_id, token):
		return False, "Failed to store request token"
	
	# now go and authorize the token
	_log_debug("redirecting to authorize token")
	bottle.redirect(smart.auth_redirect_url)
	return True, None


def _exchange_token(req_token, verifier):
	""" Takes the request token and the verifier, obtained in our authorize callback, and exchanges it for an access
	token.
	Stores the access token and returns a tuple with the cookie key, api_base and record_id.
	"""
	ts = TokenStore()
	full_token, api_base, record_id = ts.tokenServerRecordForToken(req_token)
	if record_id is None:
		_log_error("Unknown token, cannot exchange %s" % req_token)
		return None, None, None
	
	# exchange the token
	_log_debug("exchange token: %s" % full_token)
	smart = _smart_client(api_base, record_id)
	if smart is None:
		return None, None, None
	
	smart.update_token(full_token)
	try:
		acc_token = smart.exchange_token(verifier)
	except Exception, e:
		_log_error("token exchange failed: %s" % e)
		return None, api_base, None
	
	# success, store it
	_log_debug("did exchange token: %s" % acc_token)
	cookie = ts.storeTokenForRecord(api_base, record_id, acc_token)
	smart.update_token(acc_token)
	
	return cookie, api_base, record_id


def _testrecord_from_request(request):
	""" Returns a "TestRecord" instance from the cookie in the request.
	"""
	if request is None:
		return None
	
	# read the cookie
	cookie = request.get_cookie(_cookie_name)
	if cookie is None:
		return None
	
	# get the token
	ts = TokenStore()
	token, api_base, record_id = ts.tokenServerRecordForCookie(cookie)
	
	record = None
	if record_id is not None:
		smart_client = _smart_client(api_base, record_id)
		if smart_client is not None:
			smart_client.update_token(token)
			record = TestRecord(smart_client)
	
	return record


# ------------------------------------------------------------------------------ Index
@app.get('/')
@app.get('/index.html')
def index():
	""" The index page makes sure we select a patient and we have a token """
	api_base = bottle.request.query.get('api_base')
	record_id = bottle.request.query.get('record_id')
	
	# no endpoint, show selector
	if api_base is None:
		_log_debug('redirecting to endpoint selection')
		bottle.redirect('endpoint_select')
	
	# no record id, call launch page
	if record_id is None:
		smart = _smart_client(api_base, record_id)
		if smart is None:
			return "Cannot connect to SMART sandbox"
		
		launch = smart.launch_url
		if launch is None:
			return "Unknown app start URL, cannot launch without an app id"
		
		_log_debug('redirecting to app launch page')
		bottle.redirect(launch)
		return
	
	# do we have a token?
	did_fetch, error_msg = _request_token_if_needed(bottle.request, record_id, api_base)
	if did_fetch:
		return		# the call above will redirect if true anyway, but let's be sure to exit here
	if error_msg:
		return error_msg
	
	# render index
	template = _jinja.get_template('index.html')
	return template.render(api_base=api_base, record_id=record_id)


@app.get('/endpoint_select')
def endpoint():
	""" Shows all possible endpoints, sending the user back to index when one is chosen """
	
	# get the callback
	# NOTE: this is done very cheaply, we need to make sure to end the url with either "?" or "&"
	callback = bottle.request.query.get('callback', 'index.html?')
	if '?' != callback[-1] and '&' != callback[-1]:
		callback += '&' if '?' in callback else '?'
	
	available = []
	for srvr in ENDPOINTS:
		available.append(srvr)
	
	# render selections
	template = _jinja.get_template('endpoint_select.html')
	return template.render(endpoints=available, callback=callback)
	


# ------------------------------------------------------------------------------ Authorization
@app.get('/authorize')
def authorize():
	""" Extract the oauth_verifier and exchange it for an access token """
	req_token = {'oauth_token': bottle.request.query.get('oauth_token')}
	verifier = bottle.request.query.get('oauth_verifier')
	cookie, api_base, record_id = _exchange_token(req_token, verifier)
	if cookie is not None:
		_log_debug('setting cookie')
		bottle.response.set_cookie(_cookie_name, cookie, path='/', max_age=24*3600)
		bottle.redirect('/index.html?api_base=%s&record_id=%s' % (api_base, record_id))
	
	# just default to showing the authorize page if we're still here
	return _serve_static('authorize.html', 'static')


# ------------------------------------------------------------------------------ RESTful paths
@app.get('/rules/')
def rules(rule_id=None):
	""" Returns all available rules """
	record = _testrecord_from_request(bottle.request)
	return json.dumps(Rule.load_rules(record), cls=JSONRuleEncoder)

@app.get('/rules/<rule_id>/run')
def run_rule(rule_id):
	""" This runs the given rule against the currently active record """
	rule = Rule.rule_named(rule_id)
	if rule is None:
		bottle.abort(404)
	
	record = _testrecord_from_request(bottle.request)
	if record is None:
		bottle.abort(400)
	
	return 'match' if rule.match_against(record) else 'ok'

@app.get('/demographics')
def demographics():
	""" Returns the current patient's demographics as JSON-LD """
	record = _testrecord_from_request(bottle.request)
	
	# turn demographics (they come as RDF graph) into JSON-LD
	d = {}
	demo_graph = record.demographics
	demo_ld = json.loads(demo_graph.serialize(format='json-ld'))
	for gr in demo_ld.get("@graph", []):
		if "sp:Demographics" == gr.get("@type"):
			d = gr
			break
	return d

@app.get('/prefill/<section_ids>')
def prefill(section_ids):
	""" Returns the data used to prefill a given processing section, JSON encoded.
	"section_ids" are chained using "+"
	"""
	record = _testrecord_from_request(bottle.request)
	if record is None or section_ids is None:
		bottle.abort(400)
	
	# collect all needed section data
	sections = section_ids.split('+')
	data = {'matches': record.stored_rule_results}			# adds the previous rule matches
	if len(sections) > 0:
		for section_id in sections:
			sect = record.prefill_data_for(section_id)
			if sect is not None:
				data.update(sect)
	
	# JSON-encode the response
	# print data
	data = json.dumps(data)
	
	return data


# ------------------------------------------------------------------------------ Static requests
@app.get('/static/<filename>')
def static(filename):
	return _serve_static(filename, 'static')

@app.get('/templates/<ejs_name>.ejs')
def ejs(ejs_name):
	return _serve_static('%s.ejs' % ejs_name, 'templates')
