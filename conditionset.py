#!/usr/bin/env python
#
#	2013-01-30	Created by Pascal Pfiffner
#


class ConditionSet(set):
	""" A set of conditions.
	
	Holds a number of "Condition" objects and can determine whether it maches them all or just one of them. Can be one
	of two types, either "all" or "any".
	"""
	
	def __init__(self, my_type, conditions=[]):
		if my_type not in ["all", "any"]:
			raise Exception('Must be of type "all" or "any", but I got "%s"' % my_type)
		self.type = my_type
		
		if len(conditions) > 0:
			for cond in conditions:
				pass
		
