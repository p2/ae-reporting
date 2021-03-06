#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	2013-01-30	Created by Pascal Pfiffner
#


import datetime

from jinja2 import Template
from jinja2 import Environment, PackageLoader
_action_env = Environment(loader=PackageLoader('action', 'forms'), trim_blocks=True)


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
		self.name = None
		self.form = None
		self.target = 'output'
		
		if from_json is not None:
			self.name = from_json.get('name')
			self.form = from_json.get('form')
			self.target = from_json.get('target')
		
	
	# -------------------------------------------------------------------------- Executing
	def execute_for(self, patient):
		""" Perform the action on the given patient """
		if self.form is None or self.target is None:
			raise Exception("I need a template and a target in order to execute")
		
		# load the form
		form = _action_env.get_template(self.form)
		return form.render(patient=patient, date=datetime.datetime.utcnow())
		
