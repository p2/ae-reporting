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
from umls import UMLS


# sandbox default setting for testing purposes
APP_ID = 'ae-reporting@apps.chip.org'
API_BASE = 'http://127.0.0.1:7000'
#API_BASE = 'http://sandbox-rest.smartplatforms.org:7000'
OAUTH_PARAMS = {
	'consumer_key': 'ae-reporting@apps.chip.org',
	'consumer_secret': 'NUzwBOMCPPxhfUQl'
}


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
	UMLS.import_snomed_if_necessary()
	
	# load all rules
	rules = load_rules()
	if len(rules) < 1:
		print "There are no rules, no point in continuing"
		print forever_alone()
		sys.exit(0)
	
	# init our client
	print '->  Connecting to SMART'
	smart = SMARTClient(APP_ID, API_BASE, OAUTH_PARAMS)
	
	# loop over all records and test against our rules
	for record_id in smart.loop_over_records():
		#if '665677' != record_id:
		#	continue
		
		record = TestRecord(smart)
		print '->  Record', record
		for rule in rules:
			print '-->  Testing against', rule
			if rule.match_against(record):
				print '==>  Record %s matches rule %s' % (record_id, rule.name)
	
	
