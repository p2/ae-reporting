#!/usr/bin/env python
#
#	2013-01-29	Created by Pascal Pfiffner
#


class TestRecord(object):
	""" Encapsulates a SMART client object so it can be handled like a record and tested against our rules """
	
	def __init__(self, smart_client):
		self.smart = smart_client
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
	
	
	# -------------------------------------------------------------------------- Utilities
	def __unicode__(self):
		return '<testrecord.TestRecord %s>' % (self.record_id)
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	def __repr__(self):
		return str(self)
