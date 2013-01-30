#!/usr/bin/env python
#
#	2013-01-30	Created by Pascal Pfiffner
#


from condition import Condition


class ConditionSet(object):
	""" A set of conditions.
	
	Holds a number of "Condition" objects and can determine whether it maches them all or just one of them. Can be one
	of two types, either "all" or "any".
	
	Can't be a subclass of "set" because I then can't add it to lists... :P
	"""
	
	def __init__(self, my_type, conditions=[]):
		if my_type not in ["all", "any"]:
			raise Exception('Must be of type "all" or "any", but I got "%s"' % my_type)
		self.type = my_type
		
		new_conds = []
		if len(conditions) > 0:
			for cond_dict in conditions:
				cond = Condition(cond_dict)
				new_conds.append(cond)
		self.conditions = new_conds
	
	def add(self, condition):
		""" Add a condition to our set """
		self.conditions.append(condition)
	
	
	def __unicode__(self):
		conds = [unicode(c) for c in self.conditions]
		return '"%s" of %s' % (self.type, conds)
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	def __repr__(self):
		return str(self)

