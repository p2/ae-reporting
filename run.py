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

# run in background? -b flag does that
BG = True if len(sys.argv) > 1 and '-b' == sys.argv[1] else False

# import settings
settings_file = 'settings_background.py' if BG else 'settings.py'
if not os.path.exists(settings_file):
	print "x>  You haven't created the file '%s'. Look at settings.py.default and copy it to %s." % (settings_file, settings_file)
	sys.exit(1)

if BG:
	from settings_background import ENDPOINTS
else:
	from settings import ENDPOINTS


def forever_alone():
	with open('forever.txt') as handle:
		return handle.read()


# if run as a script, we kick in here
if __name__ == "__main__":
	UMLS.import_snomed_if_necessary()
	
	if BG:
		print "->  Running as a background app"
	
	# load all rules
	rules = Rule.load_rules()
	if len(rules) < 1:
		print "There are no rules, no point in continuing"
		print forever_alone()
		sys.exit(1)
	print "->  Did load %d %s" % (len(rules), 'rule' if 1 == len(rules) else 'rules')
	
	# multiple endpoints? Ask which one to use
	ep_url = None
	if len(ENDPOINTS) > 1:
		print "->  These are the available SMART containers:"
		i = 0
		for ep_base, dictionary in ENDPOINTS.iteritems():
			i += 1
			print '    [%d]  %s (%s)' % (i, dictionary.get('name'), ep_base)
		
		# ask for one
		while ep_url is None:
			use_ep = raw_input("Which SMART container do you want to use? ")
			use_ep = int(use_ep) - 1
			try:
				ep_url = ENDPOINTS.keys()[use_ep]
			except:
				pass
	
	# only one endpoint, use it
	elif len(ENDPOINTS) > 0:
		ep_url = ENDPOINTS.keys()[0]
	
	if ep_url is None:
		print "x>  There are no SMART containers configured, stopping here"
		print forever_alone()
		sys.exit(1)
	
	# init SMART client
	ep = ENDPOINTS.get(ep_url)
	smart = SMARTClient(ep.get('app_id'), ep_url, ep)
	
	
	# -------------------------------------------------------------------------- Background App
	# loop over all records and test against our rules
	if BG:
		for record_id in smart.loop_over_records():
			record = TestRecord(smart)
			print "->  Record", record.record_id
			for rule in rules:
				print "-->  Testing against", rule.name
				if rule.match_against(record):
					print "==>  Record %s matches rule %s" % (record_id, rule.name)
					print rule.perform_actions(record)
		sys.exit(0)
	
	
	# -------------------------------------------------------------------------- Record Scoped
	smart.record_id = '665677'
	ts = TokenStore()
	known_token = ts.tokenForRecord(ep_url, smart.record_id)
	
	# request a token for a specific record id
	if known_token is None:
		token = smart.fetch_request_token()
		ts.storeTokenForRecord(ep_url, smart.record_id, token)
		
		print "->  Now visit:  %s" % smart.auth_redirect_url
		Popen(['open', smart.auth_redirect_url])
		oauth_verifier = raw_input("Enter the oauth_verifier: ")
		
		# exchange and store the token
		token = smart.exchange_token(oauth_verifier)
		if token and token.get('oauth_token') and token.get('oauth_token_secret'):
			ts.storeTokenForRecord(ep_url, smart.record_id, token)
	else:
		print "->  Reusing existing access token"
		smart.update_token(known_token)
	
	# create a patient and test it against our rules
	record = TestRecord(smart)
	print "->  Record", record.record_id
	for rule in rules:
		print "-->  Testing against", rule.name
		if rule.match_against(record):
			print "==>  Record %s matches rule %s" % (smart.record_id, rule.name)
			print rule.perform_actions(record)
