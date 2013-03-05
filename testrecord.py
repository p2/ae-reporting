#!/usr/bin/env python
#
#	2013-01-29	Created by Pascal Pfiffner
#


import json
from rdflib.graph import Graph

from rule import JSONRuleEncoder


class TestRecord(object):
	""" Encapsulates a SMART client object so it can be handled like a record and tested against our rules """
	
	def __init__(self, smart_client):
		self.smart = smart_client
		self.matches = {}				# conditions write the matched objects to arrays by system key
		self._demographics = None
		self._medications = None
		self._problems = None
		self._vitals = None
		self._scratchpad_data = None
	
	
	# -------------------------------------------------------------------------- Properties
	@property
	def record_id(self):
		return self.smart.record_id
	
	@property
	def demographics(self):
		if self._demographics is None:
			ret = self.smart.get_demographics()
			status = ret.response.get('status')
			if '200' != status:
				raise Exception("Failed to get demographics: %s" % status)
			self._demographics = ret.graph
		
		return self._demographics
	
	@property
	def medications(self):
		if self._medications is None:
			ret = self.smart.get_medications()
			status = ret.response.get('status')
			if '200' != status:
				raise Exception("Failed to get medications: %s" % status)
			#self._medications.serialize(destination="medications-%s.rdf" % self.record_id)
			self._medications = ret.graph
		
		return self._medications
	
	@property
	def problems(self):
		if self._problems is None:
			ret = self.smart.get_problems()
			status = ret.response.get('status')
			if '200' != status:
				raise Exception("Failed to get problems: %s" % status)
			#self._problems.serialize(destination="problems-%s.rdf" % self.record_id)
			self._problems = ret.graph
		
		return self._problems
	
	@property
	def vitals(self):
		if self._vitals is None:
			ret = self.smart.get_vital_sign_sets()
			status = ret.response.get('status')
			if '200' != status:
				raise Exception("Failed to get vitals: %s" % status)
			#self._vitals.serialize(destination="vitals-%s.rdf" % self.record_id)
			self._vitals = ret.graph
		
		return self._vitals
	
	
	# -------------------------------------------------------------------------- Running Rules
	def prepare_rule_run(self, rule):
		self.matches = {}
	
	def matches_for(self, rule):
		return self.matches
	
	def did_match_item(self, item, condition):
		""" The conditions should call this so the instance can properly fill an ivar for the given item
		"""
		if item is not None and condition.id is not None:
			matches = self.matches.get(condition.id, [])
			matches.append(item)
			self.matches[condition.id] = matches
	
	
	# -------------------------------------------------------------------------- Object Extraction
	def graph_for(self, data_type):
		""" calls the appropriate property getter for the given data type """
		
		if '<http://smartplatforms.org/terms#Medication>' == data_type:
			return self.medications
		if '<http://smartplatforms.org/terms#Problem>' == data_type:
			return self.problems
		return None
	
	def get_object_for(self, item, item_system):
		""" Get the interesting parts for an item, depending on its system
		"""
		
		# fetch the item
		body = self.fetch_item(item)		# maybe use self.medications or self.problems?
		if body is None:
			return None
		
		graph = Graph()
		graph.parse(data=body, publicID=item)
		
		return self.data_from_graph(graph, item_system)
	
	def data_from_graph(self, graph, item_system):
		""" Creates (JSON-encodable) data from a given graph representing a given item
		"""
		
		# a medication
		if 'rxnorm' == item_system:
			sparql = """
				PREFIX sp: <http://smartplatforms.org/terms#>
				PREFIX dcterms: <http://purl.org/dc/terms/>
				SELECT ?code ?name ?start_date ?end_date
				WHERE {
					?item sp:drugName ?name_node .
					?name_node sp:code ?code .
					OPTIONAL { ?name_node dcterms:title ?name . }
					OPTIONAL { ?item sp:startDate ?start_date . }
					OPTIONAL { ?item sp:endDate ?end_date . }
				}
			"""
			
			results = graph.query(sparql)
			if len(results) < 1:
				print "xxx>  get_object_for() SPARQL query for %s didn't match" % item_system
				return None
			
			res = list(results)[0]		# can't believe SPARQLQueryResult doesn't reply to "next()"...
			
			return {
				"rxnorm": res[0],
				"name": res[1],
				"start_date": res[2],
				"end_date": res[3]
			}
		
		# SNOMED problems
		if 'snomed' == item_system:
			sparql = """
				PREFIX sp: <http://smartplatforms.org/terms#>
				PREFIX dcterms: <http://purl.org/dc/terms/>
				SELECT ?code ?name ?start_date ?end_date
				WHERE {
					?item sp:problemName ?name_node .
					?name_node sp:code ?code .
					OPTIONAL { ?name_node dcterms:title ?name . }
					OPTIONAL { ?item sp:startDate ?start_date . }
					OPTIONAL { ?item sp:endDate ?end_date . }
				}
			"""
			
			results = graph.query(sparql)
			if len(results) < 1:
				print "xxx>  get_object_for() SPARQL query for %s didn't match" % item_system
				return None
			
			res = list(results)[0]
			
			return {
				"snomed": res[0],
				"name": res[1],
				"start_date": res[2],
				"end_date": res[3]
			}
		
		return None
	
	def fetch_item(self, item_url):
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
	
	
	# -------------------------------------------------------------------------- Rule Prefill
	def prefill_data_for(self, section_id):
		""" Fetches the SMART data associated with the given section id
		"""
		
		# demographics additionally wants vitals, so we return both
		if 'demographics' == section_id:
			demo_graph = self._prefill_graph_for('demographics')
			demo_ld = json.loads(demo_graph.serialize(format='json-ld'))
			demo = {}
			for gr in demo_ld.get("@graph", []):
				if "sp:Demographics" == gr.get("@type"):
					demo = gr
					break
			
			# vitals
			vitals_graph = self._prefill_graph_for('vitals')
			vitals_ld = json.loads(vitals_graph.serialize(format='json-ld'))
			vitals = []
			for vset in vitals_ld.get("@graph", []):
				if "sp:VitalSignSet" == vset.get("@type"):
					vitals.append(vset)
			
			# sort latest first
			demo['vitals'] = sorted(vitals, key=lambda k: k['dcterms:date'], reverse=True)
			
			return demo
		
		# non-special linear graphs
		graph = self._prefill_graph_for(section_id)
		if graph is None:
			return {}
		
		return self.data_from_graph(graph, section_id)
	
	def _prefill_graph_for(self, section_id):
		""" Fetches the SMART RDF graph associated with the given section id
		"""
		
		# demographics also needs vitals
		if 'demographics' == section_id:
			return self.demographics
		if 'vitals' == section_id:
			return self.vitals
		
		print "I don't know what graph to return for section", section_id
		return None
	
	
	# -------------------------------------------------------------------------- App Storage	
	@property
	def scratchpad_data(self):
		if self._scratchpad_data is None:
			self._scratchpad_data = self.get_scratchpad_data()
		return self._scratchpad_data
	
	@scratchpad_data.setter
	def scratchpad_data(self, new_data):
		if self.set_scratchpad_data(new_data):
			self._scratchpad_data = new_data
	
	
	@property
	def stored_rule_results(self):
		storage = self.scratchpad_data
		if storage is not None:
			return storage.get('rules')
		return None
	
	@stored_rule_results.setter
	def stored_rule_results(self, new_rules={}):
		storage = self.scratchpad_data
		if new_rules is None or len(new_rules) > 0:
			if storage is None:
				storage = {}
			storage['rules'] = new_rules
		
		self.scratchpad_data = storage
	
	
	def store_new_result_for_rule(self, result, rule):
		""" Stores the given result to SMART scratchpad data """
		
		if result is not None and rule is not None:
			stored = self.stored_rule_results
			if stored is None:
				stored = {}
			
			mine = stored.get(rule.id, [])
			mine.append(result)
			stored[rule.id] = mine
			
			self.stored_rule_results = stored
	
	def get_scratchpad_data(self):
		try:
			res = self.smart.get_scratchpad_data()
			# print 'LOADED SCRATCHPAD', res.body
			if res.body is None or len(res.body) < 1:
				return None
			return json.loads(res.body)
		except Exception, e:
			print e
		return None
	
	def set_scratchpad_data(self, data):
		try:
			if data is not None:
				encoded = json.dumps(data, cls=JSONRuleEncoder)
				# print 'STORING SCRATCHPAD', encoded
				res = self.smart.put_scratchpad_data(encoded)
				print res.response
			else:
				# print 'DELETING SCRATCHPAD'
				res = self.smart.delete_scratchpad_data()
				print res.response
			return True
		except Exception, e:
			print e
		return False
	
	
	# -------------------------------------------------------------------------- Utilities
	def __unicode__(self):
		return '<testrecord.TestRecord %s>' % (self.record_id)
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	def __repr__(self):
		return str(self)
