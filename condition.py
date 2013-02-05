#!/usr/bin/env python
#
#	2013-01-29	Created by Pascal Pfiffner
#


from matcher import Matcher
from testrecord import TestRecord
from lookup import Lookup


class Condition(Matcher):
	""" A Condition
	"""
	
	def __init__(self, from_dict=None):
		if from_dict is not None:
			self.system = from_dict.get('system')
			self.subject = from_dict.get('subject')
			self.predicate = from_dict.get('predicate')
			self.object = from_dict.get('object')
	
	
	# -------------------------------------------------------------------------- Testing
	def match_against(self, patient):
		graph = patient.graph_for(self.subject)
		if graph is None:
			return False
		
		item_sparql = self.sparql_query_for_item_of_system()
		if item_sparql is None:
			raise Exception("I don't know how to extract items for '%s'" % self.system)
		
		# extract the actual items that we want to test against
		query = """
			PREFIX sp:<http://smartplatforms.org/terms#>
			SELECT ?item
			WHERE {
				?var1 a %s .
				%s
			}
		""" % (self.subject, item_sparql)
		items = graph.query(query)
		
		if len(items) < 1:
			return False
		
		# get our lookup system
		lookup = Lookup.for_system(self.system)
		if lookup is None:
			raise Exception("We don't have a lookup system for '%s'" % self.system)
		
		# test the quality of our items (remember "items" is full of tuples from the sparql query)
		for item in items:
			if lookup.has_relation(item[0], self.predicate, self.object):
				print '===>  Matches', self
				return True
		
		return False
	
	
	def sparql_query_for_item_of_system(self):
		if 'rxnorm' == self.system:
			return """
				?var1 sp:drugName ?var2 .
				?var2 sp:code ?item .
			"""
		if 'snomed' == self.system:
			return """
				?var1 sp:problemName ?var2 .
				?var2 sp:code ?item .
			"""
		return None
			
	
	
	# -------------------------------------------------------------------------- Utilities
	def __unicode__(self):
		return '%s %s %s' % (self.subject, self.predicate, self.object)
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	def __repr__(self):
		return str(self)
		
