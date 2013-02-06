#!/usr/bin/env python
#
#	2013-01-29	Created by Pascal Pfiffner
#


class TestRecord(object):
	""" Encapsulates a SMART client object so it can be handled like a record and tested against our rules """
	
	def __init__(self, smart_client):
		self.smart = smart_client
		self.matches = {}				# conditions write the matched objects to arrays by system key
		self._medications = None
		self._problems = None
	
	@property
	def record_id(self):
		return self.smart.record_id
	
	
	# -------------------------------------------------------------------------- Properties
	@property
	def medications(self):
		if self._medications is None:
			self._medications = self.smart.get_medications()
			#self._medications.graph.serialize(destination="medications-%s.rdf" % self.record_id)
		return self._medications
	
	
	@property
	def problems(self):
		if self._problems is None:
			self._problems = self.smart.get_problems()
			#self._problems.graph.serialize(destination="problems-%s.rdf" % self.record_id)
		return self._problems
	
	
	# -------------------------------------------------------------------------- Matching data models to properties
	def graph_for(self, data_type):
		""" calls the appropriate property getter for the given data type """
		
		if '<http://smartplatforms.org/terms#Medication>' == data_type:
			return self.medications.graph
		if '<http://smartplatforms.org/terms#Problem>' == data_type:
			return self.problems.graph
		return None
	
	def did_match_item(self, item, item_system):
		""" The conditions should call this so the instance can properly fill an ivar for the given item
		"""
		to_store = self.get_object_for(item, item_system)
		if to_store is not None:
			matches = self.matches.get(item_system, [])
			matches.append(to_store)
			self.matches[item_system] = matches
	
	
	# -------------------------------------------------------------------------- Object Extraction
	def get_object_for(self, item, item_system):
		""" Get the interesting parts for an item, depending on its system
		"""
		
		# a medication, get the code, name, start- and end-date
		if 'rxnorm' == item_system:
			med = self.get_item(item)
			if med is None:
				return None
			print med
			return {
				"rxnorm": item,
				"name": "A medication",
				"start_date": None,
				"end_date": None
			}
		
		# SNOMED problems
		if 'snomed' == item_system:
			prob = self.get_item(item)
			if prob is None:
				return None
			print prob
			return {
				"snomed": item,
				"name": "A problem",
				"start_date": None
			}
		
		return None
	
	def get_item(self, item_url):
		""" Uses the SMART client to GET RDF for an item
		"""
		
		body = None
		try:
			head, body = self.smart.get(item_url)
			if head.get('status') != '200':
				print 'Failed to GET "%s": %s' % (item_url, head.get('status'))
				return None
		except Exception, e:
			print 'Failed to GET "%s": %s' % (item_url, e)
			return None
		
		return body
	
	
	# -------------------------------------------------------------------------- Utilities
	def __unicode__(self):
		return '<testrecord.TestRecord %s>' % (self.record_id)
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	def __repr__(self):
		return str(self)
