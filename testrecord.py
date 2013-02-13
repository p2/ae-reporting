#!/usr/bin/env python
#
#	2013-01-29	Created by Pascal Pfiffner
#


from rdflib.graph import Graph


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
			status = self._medications.response.get('status')
			if '200' != status:
				raise Exception("Failed to get medications: %s" % status)
			#self._medications.graph.serialize(destination="medications-%s.rdf" % self.record_id)
		return self._medications
	
	
	@property
	def problems(self):
		if self._problems is None:
			self._problems = self.smart.get_problems()
			status = self._problems.response.get('status')
			if '200' != status:
				raise Exception("Failed to get problems: %s" % status)
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
		
		# fetch the item
		body = self.fetch_item(item)		# maybe use self.medications or self.problems?
		if body is None:
			return None
		
		graph = Graph()
		graph.parse(data=body, publicID=item)
		
		# a medication
		if 'rxnorm' == item_system:
			
			# extract interesting properties
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
			
			# extract interesting properties
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
	
	
	# -------------------------------------------------------------------------- Utilities
	def __unicode__(self):
		return '<testrecord.TestRecord %s>' % (self.record_id)
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	def __repr__(self):
		return str(self)
