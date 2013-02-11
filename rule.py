#!/usr/bin/env python
#
#	2013-01-30	Created by Pascal Pfiffner
#


import os.path
import glob
import json

from matcher import Matcher
from conditionset import ConditionSet
from action import Action


class Rule(Matcher):
	""" A Rule
	
	A rule is a set of condition-sets, which can be nested and in turn contain other condition-sets or actual
	conditions. The rule itself has one top-level condition-set which is an "all" condition set.
	"""
	
	@classmethod
	def load_rules(cls):
		""" Loads all bundled rules """
		rules = []
		
		# find all files starting with "rule-*.json"
		mydir = os.path.realpath(os.getcwd())
		for rule_file in glob.glob('rules/rule-*.json'):
			with open(rule_file) as handle:
				rule_json = handle.read()
				rule = cls(json.loads(rule_json))
				rules.append(rule)
		
		return rules

	def __init__(self, from_json=None):
		if from_json is not None:
			self.scope = from_json.get('scope')
			self.name = from_json.get('name')
			self.description = from_json.get('description')
			
			cond_dict = from_json.get('condition')
			self.condition = ConditionSet(cond_dict)
			
			action_dict = from_json.get('actions')
			self.actions = Action.from_array(action_dict)
		else:
			self.name = None
			self.condition = None
			self.actions = []
	
	
	# -------------------------------------------------------------------------- Matching and Acting
	def match_against(self, patient):
		return self.condition.match_against(patient)
	
	def perform_actions(self, patient):
		for action in self.actions:
			action.execute_for(patient)
	
	
	# -------------------------------------------------------------------------- Utilities
	def __unicode__(self):
		return '<rule.Rule %s>' % self.name
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	def __repr__(self):
		return str(self)


class JSONRuleEncoder(json.JSONEncoder):
	""" Encode a rule as JSON easily """
	
	def default(self, rule):
		if isinstance(rule, Rule):
			return {
				"name": rule.name,
				"description": rule.description,
				"scope": rule.scope
			}
		return json.JSONEncoder.default(self, rule)


