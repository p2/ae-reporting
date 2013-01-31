#!/usr/bin/env python
#
#	2013-01-28	Created by Pascal Pfiffner
#

import oauth2 as oauth
import time
import sys
import os
import os.path
import glob
import json
from subprocess import Popen

from smart_client_python.client import SMARTClient
from rule import Rule
from testrecord import TestRecord


# sandbox default setting for testing purposes
#API_BASE = 'http://coruscant.local:7000'
API_BASE = 'http://sandbox-rest.smartplatforms.org:7000'
OAUTH_PARAMS = {
	'consumer_key': 'ae-reporting@apps.chip.org',
	'consumer_secret': 'fNpKMtZEhnhLGJqO'
}

KNOWN_TOKENS = {}


def load_rules():
	""" Loads all bundled rules """
	rules = []
	
	# find all files starting with "rule-*.json"
	mydir = os.path.realpath(os.getcwd())
	for rule_file in glob.glob('rule-*.json'):
		with open(rule_file) as handle:
			rule_json = handle.read()
			rule = Rule(json.loads(rule_json))
			rules.append(rule)
	
	return rules

def forever_alone():
	with open('forever.txt') as handle:
		return handle.read()
	


# if run as a script, we kick in here
if __name__ == "__main__":
	
	# load all rules
	rules = load_rules()
	if len(rules) < 1:
		print "There are no rules, no point in continuing"
		print forever_alone()
		sys.exit(0)
	
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
	
	# create a patient and test it against our rules
	patient = TestRecord(smart)
	print '->  Patient', patient
	for rule in rules:
		print '-->  Testing against', rule
		rule.match_against(patient)
	
	
