#!/usr/bin/env python
#
#	2013-01-30	Created by Pascal Pfiffner
#


import os.path
import glob
import json

from matcher import Matcher
from conditionset import ConditionSet
from condition import Condition
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
			rule_id_full = os.path.basename(rule_file)
			rule_id = rule_id_full.replace('.json', '').replace('rule-', '')
			
			# load the rule
			rule = cls._rule_from_file(rule_id, rule_file)
			if rule:
				rules.append(rule)
		
		return rules
	
	@classmethod
	def rule_named(cls, rule_name):
		""" Loads the given rule """
		rule = None
		filepath = 'rules/rule-%s.json' % rule_name.replace('/', '')
		
		# if the file exists, load the rule
		if os.path.exists(filepath):
			rule = cls._rule_from_file(rule_name, filepath)
		
		return rule		
	
	@classmethod
	def _rule_from_file(cls, rule_id, filepath):
		""" Load a rule from a given file.
		The file must exist, it is not checked! """
		
		rule = None
		with open(filepath) as handle:
			rule_json = handle.read()
			rule = cls(rule_id, json.loads(rule_json))
		
		return rule
	
	
	def __init__(self, rule_id, from_json=None):
		self.id = rule_id
		
		if from_json is None:
			from_json = {}
		
		self.scope = from_json.get('scope')
		self.name = from_json.get('name')
		self.description = from_json.get('description')
		self.references = from_json.get('references', [])
		
		cond_dict = from_json.get('condition')
		self.condition = Condition(cond_dict) if 'subject' in cond_dict else ConditionSet(cond_dict)
		
		action_dict = from_json.get('actions')
		self.actions = Action.from_array(action_dict)
	
	
	# -------------------------------------------------------------------------- Matching and Acting
	def match_against(self, patient):
		return self.condition.match_against(patient)
	
	def perform_actions(self, patient):
		results = []
		for action in self.actions:
			result = action.execute_for(patient)
			if result is not None:
				results.append(result)
		
		return results
	
	
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
				"id": rule.id,
				"name": rule.name,
				"description": rule.description,
				"scope": rule.scope
			}
		return json.JSONEncoder.default(self, rule)


