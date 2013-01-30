#!/usr/bin/env python
#
#	2013-01-30	Created by Pascal Pfiffner
#


from matcher import Matcher
from conditionset import ConditionSet


class Rule(Matcher):
	""" A Rule
	
	A rule is a set of condition-sets, which can be nested and in turn contain other condition-sets or actual
	conditions. The rule itself has one top-level condition-set which is an "all" condition set.
	"""
	
	def __init__(self, from_json=None):
		if from_json is not None:
			self.scope = from_json.get('scope')
			self.name = from_json.get('name')
			self.description = from_json.get('description')
			
			rule = from_json.get('rule')
			self.condition = ConditionSet('all')
			if len(rule.get('all', [])) > 0:
				all_cond = ConditionSet('all', rule.get('all'))
				self.condition.add(all_cond)
			if len(rule.get('any', [])) > 0:
				any_cond = ConditionSet('any', rule.get('any'))
				self.condition.add(any_cond)
			
			self.actions = []
	
	
	# -------------------------------------------------------------------------- Testing
	def match_against(self, patient):
		return self.condition.match_against(patient)
	
	
	# -------------------------------------------------------------------------- Utilities
	def __unicode__(self):
		return '<rule.Rule %s>' % self.name
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	def __repr__(self):
		return str(self)

