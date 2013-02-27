#!/usr/bin/env python
#
#	2013-01-30	Created by Pascal Pfiffner
#


import os.path
import glob
import json
import datetime

from matcher import Matcher
from conditionset import ConditionSet
from condition import Condition
from action import Action


class Rule(Matcher):
	""" A Rule
	
	A rule is a set of condition-sets, which can be nested and in turn contain other condition-sets or actual
	conditions. The rule itself has one top-level condition-set which is an "all" condition set.
	"""
	
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
		
		self.last_results = None
	
	def json(self):
		return json.dumps(self, cls=JSONRuleEncoder)
	
	
	@classmethod
	def load_rules(cls, patient=None):
		""" Loads all bundled rules """
		rules = []
		old_results = None
		
		# get old results
		if patient is not None:
			old_results = patient.stored_rule_results
		
		# find all files starting with "rule-*.json"
		mydir = os.path.realpath(os.getcwd())
		for rule_file in glob.glob('rules/rule-*.json'):
			rule_id_full = os.path.basename(rule_file)
			rule_id = rule_id_full.replace('.json', '').replace('rule-', '')
			
			# load the rule
			rule = cls._rule_from_file(rule_id, rule_file)
			if rule:
				rules.append(rule)
				
				# has it been run against the patient before?
				if old_results is not None:
					rule.last_results = RuleResult.from_json_array(rule, old_results.get(rule.id))
		
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
	
	
	# -------------------------------------------------------------------------- Matching and Acting
	def run_against(self, patient):
		""" Runs the rule and, if it matches, runs the actions.
		Also stores the run info on the server. """
		
		flag = self.match_against(patient)
		results = []
		if flag:
			results = self.perform_actions(patient)
		
		# store this new result
		new_result = RuleResult(self, None, flag, results)
		self.store_new_result_for(new_result, patient)
		
		return results if len(results) > 0 else 0
	
	def match_against(self, patient):
		return self.condition.match_against(patient)
	
	def perform_actions(self, patient):
		""" Returns an array of result actions """
		
		results = []
		for action in self.actions:
			result = action.execute_for(patient)
			if result is not None:
				results.append(result)
		
		return results
	
	
	# -------------------------------------------------------------------------- Storing
	def store_new_result_for(self, result, patient):
		""" Stores the given result to SMART scratchpad data """
		
		if result is not None and patient is not None:
			stored = patient.stored_rule_results
			if stored is None:
				stored = {}
			
			mine = stored.get(self.id, [])
			mine.append(result)
			stored[self.id] = mine
			
			patient.stored_rule_results = stored
	
	
	# -------------------------------------------------------------------------- Utilities
	def __unicode__(self):
		return '<rule.Rule %s>' % self.name
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	def __repr__(self):
		return str(self)


class RuleResult(object):
	""" Encapsulates info on when the rule last ran and its result """
	
	def __init__(self, rule, date=None, flag=False, results=[]):
		self.rule = rule
		self.run_date = date if date is not None else datetime.datetime.utcnow()
		self.run_result_flag = flag
		self.run_results = results
	
	def json(self):
		return json.dumps(self, cls=JSONRuleResultEncoder)
	
	@classmethod
	def from_json_array(cls, rule, json_array):
		""" Expects an array full of dictionaries """
		if json_array is None or len(json_array) < 1:
			return None
		
		inst = []
		for json_dict in json_array:
			obj = cls._result_from_json(rule, json_dict)
			if obj:
				inst.append(obj)
		
		return inst
	
	@classmethod
	def _result_from_json(cls, rule, json_dict):
		if json_dict is None:
			return None
		
		date_obj = None
		date_stamp = json_dict.get('date')
		if date_stamp is not None:
			date_obj = datetime.datetime.utcfromtimestamp(float(date_stamp))
		
		return cls(rule, date_obj, json_dict.get('flag'), json_dict.get('results'))


class JSONRuleEncoder(json.JSONEncoder):
	""" Encode a rule/rule-result as JSON easily """
	
	def default(self, item):
		
		# a Rule
		if isinstance(item, Rule):
			return {
				"id": item.id,
				"name": item.name,
				"description": item.description,
				"references": item.references,
				"scope": item.scope,
				"last_results": item.last_results
			}
		
		# a RuleResult
		if isinstance(item, RuleResult):
			return {
				'date': item.run_date.strftime('%s'),
				'flag': item.run_result_flag,
				'results': item.run_results
			}
		
		# fall back
		return json.JSONEncoder.default(self, item)


