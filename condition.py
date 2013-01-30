#!/usr/bin/env python
#
#	2013-01-29	Created by Pascal Pfiffner
#


from matcher import Matcher
from testrecord import TestRecord


class Condition(Matcher):
	""" A Condition
	"""
	
	def __init__(self, from_dict=None):
		if from_dict is not None:
			self.subject = from_dict.get('subject')
			self.predicate = from_dict.get('predicate')
			self.object = from_dict.get('object')
	
	
	# -------------------------------------------------------------------------- Testing
	def match_against(self, patient):
		graph = patient.property_for(self.subject)
		print '--->  NOW MATCH AGAINST', graph
		return False
	
	
	# -------------------------------------------------------------------------- Utilities
	def __unicode__(self):
		return '%s %s %s' % (self.subject, self.predicate, self.object)
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	def __repr__(self):
		return str(self)
		
