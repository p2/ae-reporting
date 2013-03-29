#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	2013-01-29	Created by Pascal Pfiffner
#


import json
import os.path
from rdflib.graph import Graph

from rule import JSONRuleEncoder
from lookup import RxNorm


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
	
	def data_from_graph(self, graph, item_system):
		""" Creates (JSON-encodable) data from a given graph representing a given item
		"""
		
		# a medication
		if 'rxnorm' == item_system:
			sparql = """
				PREFIX sp: <http://smartplatforms.org/terms#>
				PREFIX dcterms: <http://purl.org/dc/terms/>
				SELECT ?code ?name ?start_date ?end_date ?quant_value ?quant_unit ?freq_value ?freq_unit
				WHERE {
					?item sp:drugName ?name_node .
					?name_node sp:code ?code .
					OPTIONAL { ?name_node dcterms:title ?name . }
					OPTIONAL { ?item sp:startDate ?start_date . }
					OPTIONAL { ?item sp:endDate ?end_date . }
					OPTIONAL {
						?item sp:quantity ?quant_node .
						?quant_node sp:value ?quant_value .
						?quant_node sp:unit ?quant_unit .
					}
					OPTIONAL {
						?item sp:frequency ?freq_node .
						?freq_node sp:value ?freq_value .
						?freq_node sp:unit ?freq_unit .
					}
				}
			"""
			
			results = graph.query(sparql)
			if len(results) < 1:
				print "xxx>  data_from_graph() SPARQL query for %s didn't match" % item_system
				return None
			
			res = list(results)[0]		# can't believe SPARQLQueryResult doesn't reply to "next()"...
			
			return {
				"rxnorm": os.path.basename(unicode(res[0])) if res[0] else None,
				"name": unicode(res[1]) if res[1] else None,
				"start_date": unicode(res[2]) if res[2] else None,
				"end_date": unicode(res[3]) if res[3] else None,
				"quantity": "%s %s" % (res[4], res[5]) if res[4] and res[5] else None,
				"frequency": "%s%s" % (res[6], res[7]) if res[6] and res[7] else None
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
				print "xxx>  data_from_graph() SPARQL query for %s didn't match" % item_system
				return None
			
			res = list(results)[0]
			
			return {
				"snomed": unicode(res[0]) if res[0] else None,
				"name": unicode(res[1]) if res[1] else None,
				"start_date": unicode(res[2]) if res[2] else None,
				"end_date": unicode(res[3]) if res[3] else None
			}
		
		# not yet returned, should we use JSON-LD?
		return None
	
	def complement_data_for(self, med, item_system):
		""" You would use this after "data_from_graph" to look up more information about the item, e.g. fetching
		manufacturer for drugs. This changes the provided data in place (!). """
		if med is None:
			return
		
		# a medication
		if 'rxnorm' == item_system and 'rxnorm' in med:
			details = RxNorm().get_details(med['rxnorm'])
			if details is not None:
				med.update(details)
			
			# date mangling
			m_start = med['start_date'] if med['start_date'] is not None else None
			m_end = med['end_date'] if med['end_date'] is not None else None
			period = ''
			if m_start is not None:
				if m_end is None:
					period += 'Since '
				period += m_start
			if m_end is not None:
				if m_start is not None:
					period += ' - '
				else:
					period += 'Until '
				period += m_end
			
			if len(period) > 0:
				med['period'] = period
	
	
	def fetch_item(self, item_url):
		""" Uses the SMART client to GET RDF for a single item
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
		""" Fetches the SMART data associated with the given section id.
		Returns a dictionary with the section_id and maybe some additional keys.
		"""
		
		# demographics additionally wants vitals, so we return both
		if 'demographics' == section_id:
			d = {}
			demo_graph = self.demographics
			demo_ld = json.loads(demo_graph.serialize(format='json-ld'))
			for gr in demo_ld.get("@graph", []):
				if "sp:Demographics" == gr.get("@type"):
					d['demographics'] = gr
					break
			
			# vitals
			vitals_graph = self.vitals
			vitals_ld = json.loads(vitals_graph.serialize(format='json-ld'))
			vitals = []
			for vset in vitals_ld.get("@graph", []):
				if "sp:VitalSignSet" == vset.get("@type"):
					vitals.append(vset)
			
			# sort latest vitals first
			d['vitals'] = sorted(vitals, key=lambda k: k['dcterms:date'], reverse=True)
			
			return d
		
		# non-special linear graphs; we don't filter them
		graph = self._prefill_graph_for(section_id)
		if graph is None:
			return None
		
		graph_ld = json.loads(graph.serialize(format='json-ld'))
		if '@graph' in graph_ld:
			graph_ld = graph_ld['@graph']
		
		return {section_id: graph_ld}
	
	def _prefill_graph_for(self, section_id):
		""" Fetches the SMART RDF graph associated with the given section id
		"""
		
		if 'medications' == section_id:
			return self.medications
		
		print "I don't know what graph to return for section", section_id
		return None
	
	
	# -------------------------------------------------------------------------- Form Processing
	def handle_form_data(self, data):
		""" When we post data to a form, some things (like medications) are just their URL. This method goes ahead and
		fetches the full items from the SMART container and converts data in place. """
		if data is None:
			return
		
		# medications?
		if 'medications' in data:
			orig = data['medications']
			drugs = orig['drug'] if 'drug' in orig else []
			meds = []
			
			for drug in drugs:
				if not isinstance(drug, dict):
					body = self.fetch_item(drug)
					if body is not None:
						graph = Graph().parse(data=body)
						med = self.data_from_graph(graph, 'rxnorm')
						if med is not None:
							self.complement_data_for(med, 'rxnorm')
							meds.append(med)
			
			data['medications']['meds'] = meds
	
	
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
