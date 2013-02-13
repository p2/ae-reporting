#!/usr/bin/env python
#
#	2013-01-28	Created by Pascal Pfiffner
#

import oauth2 as oauth
import time
import sys
import os
import os.path
import json
from subprocess import Popen

from smart_client_python.client import SMARTClient
from tokenstore import TokenStore
from rule import Rule
from testrecord import TestRecord
from umls import UMLS

# import settings
if not os.path.exists('settings.py'):
	print "x>  You haven't created the settings.py file. Look at settings.py.default and copy it to settings.py."
	sys.exit(1)

from settings import APP_ID, API_BASE, OAUTH_PARAMS


def forever_alone():
	with open('forever.txt') as handle:
		return handle.read()


# if run as a script, we kick in here
if __name__ == "__main__":
	UMLS.import_snomed_if_necessary()
	
	# load all rules
	rules = Rule.load_rules()
	if len(rules) < 1:
		print "There are no rules, no point in continuing"
		print forever_alone()
		sys.exit(0)
	print '->  Did load %d %s' % (len(rules), 'rule' if 1 == len(rules) else 'rules')
	
	# init our client and token store
	smart = SMARTClient(APP_ID, API_BASE, OAUTH_PARAMS)
	smart.record_id = '665677'
	ts = TokenStore(API_BASE)
	known_token = ts.tokenForRecord(smart.record_id)
	
	# request a token for a specific record id
	if known_token is None:
		token = smart.fetch_request_token()
		ts.storeTokenForRecord(smart.record_id, token)
		
		print 'Now visit:  %s' % smart.auth_redirect_url
		Popen(['open', smart.auth_redirect_url])
		oauth_verifier = raw_input('Enter the oauth_verifier: ')
		
		# exchange and store the token
		token = smart.exchange_token(oauth_verifier)
		if token and token.get('oauth_token') and token.get('oauth_token_secret'):
			ts.storeTokenForRecord(smart.record_id, token)
	else:
		print '->  Reusing existing access token'
		smart.update_token(known_token)
	
	# create a patient and test it against our rules
	patient = TestRecord(smart)
	print '->  Patient', patient
	for rule in rules:
		print '-->  Testing against', rule
		if rule.match_against(patient):
			rule.perform_actions(patient)
	
	# loop over all records and test against our rules (only works as a background app)
	#for record_id in smart.loop_over_records():
	# 	record = TestRecord(smart)
	# 	print '->  Record', record
	# 	for rule in rules:
	# 		print '-->  Testing against', rule
	# 		if rule.match_against(record):
	# 			print '==>  Record %s matches rule %s' % (record_id, rule.name)
