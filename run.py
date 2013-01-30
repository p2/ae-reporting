#!/usr/bin/env python
#
#	2013-01-28	Created by Pascal Pfiffner
#

import oauth2 as oauth
import time
import sys
import os.path
import json
from subprocess import Popen

from smart_client_python.client import SMARTClient


# sandbox default setting for testing purposes
API_BASE = 'http://coruscant.local:7000'
#API_BASE = 'http://sandbox-rest.smartplatforms.org:7000'
OAUTH_PARAMS = {
	'consumer_key': 'ae-reporting@apps.chip.org',
	'consumer_secret': 'AiwnhVBSGGIHYtYG'
}

KNOWN_TOKENS = {}


# if run as a script, we kick in here
if __name__ == "__main__":
	
	# load stored tokens
	if os.path.exists('tokens.json'):
		token_json = ''
		with open('tokens.json') as handle:
			token_json = handle.read()
		KNOWN_TOKENS = json.loads(token_json)
	
	# init our client
	smart = SMARTClient(API_BASE, OAUTH_PARAMS)
	smart.record_id = '1288992'
	known_token = KNOWN_TOKENS.get(API_BASE, {}).get(smart.record_id)
	
	# request a token for a specific record id
	if known_token is None:
		smart.fetch_request_token()
		print 'Now visit:  %s' % smart.auth_redirect_url
		Popen(['open', smart.auth_redirect_url])
		oauth_verifier = raw_input('Enter the oauth_verifier: ')
		
		# exchange and store the token
		token = smart.exchange_token(oauth_verifier)
		if token and token.get('oauth_token') and token.get('oauth_token_secret'):
			if KNOWN_TOKENS.get(API_BASE) is None:
				KNOWN_TOKENS[API_BASE] = {}
			KNOWN_TOKENS[API_BASE][smart.record_id] = token
			with open('tokens.json', 'w') as handle:
				handle.write(json.dumps(KNOWN_TOKENS))
	else:
		print 'Reusing existing access token'
		smart.update_token(known_token)
	
	# get meds
	meds = smart.get_medications()
	if '200' != meds.response.get('status'):
		print "Failed to get medications: %s" % meds.response.get('status')
		sys.exit(1)
	
	graph = meds.graph
	print 'Now do something with those meds...'
	
