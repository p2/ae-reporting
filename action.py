#!/usr/bin/env python
#
#	2013-01-30	Created by Pascal Pfiffner
#


from testrecord import TestRecord


class Action(object):
	""" Defines an action to take if a Rule matches.
	"""
	
	@classmethod
	def from_array(cls, json_array):
		""" Instantiate from an array of actions
		"""
		instances = []
		if (len(json_array) > 0):
			for json in json_array:
				instances.append(Action(json))
		return instances
	
	
	def __init__(self, from_json=None):
		if from_json is not None:
			pass
	
	
	# -------------------------------------------------------------------------- Executing
	def execute_for(self, patient):
		pass
