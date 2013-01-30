#!/usr/bin/env python
#
#	2013-01-29	Created by Pascal Pfiffner
#


class Condition(object):
	""" A Condition
	"""
	
	def __init__(self, from_dict=None):
		if from_dict is not None:
			self.subject = from_dict.get('subject')
			self.predicate = from_dict.get('predicate')
			self.object = from_dict.get('object')
	
	
	def __unicode__(self):
		return '%s %s %s' % (self.subject, self.predicate, self.object)
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	def __repr__(self):
		return str(self)
		
