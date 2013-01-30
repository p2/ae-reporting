#!/usr/bin/env python
#
#	2013-01-30	Created by Pascal Pfiffner
#


from condition import Condition
from conditionset import ConditionSet


class Rule(object):
	""" A Rule
	
	A rule is a set of condition-sets, which can be nested and in turn contain other condition-sets or actual
	conditions.
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
				self.condition.append(all_cond)
			if len(rule.get('any', [])) > 0:
				any_cond = ConditionSet('any', rule.get('any'))
				self.condition.append(any_cond)
			
			self.actions = []
	
	
		
