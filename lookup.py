#!/usr/bin/env python
#
#	2013-01-31	Created by Pascal Pfiffner
#


import os.path

from sqlite import SQLite


class Lookup(object):
	""" Superclass for our coding system lookup implementations.
	"""
	
	@classmethod
	def for_system(cls, system):
		if 'rxnorm' == system:
			return RxNorm()
		if 'snomed' == system:
			return SNOMED()
		return None
	
	
	def has_relation(self, subject_id, relation, object_id):
		return False
	
	def id_from_uri(self, something):
		""" Extracts the id of an object that encodes a URI """
		if something is None:
			return None
		
		if isinstance(something, (int, long)):
			return something
		
		# get the bare URI
		uri = unicode(something)
		if '>' == uri[-1:]:
			uri = uri[1:-1]
		
		# split and return the last component
		return os.path.split(uri)[1]



# ============================================================================== RxNorm
class RxNorm(Lookup):
	""" Handling RxNorm lookups.
	"""
	
	def __init__(self):
		self.sqlite = SQLite.get('databases/rxnorm.db')
	
	
	def has_relation(self, subj, relation, obj):
		""" Checks RXNREL table for the desired relation.
		"""
		
		# get the RxNorm ids from subject and object and run the query
		subject_id = self.id_from_uri(subj)
		object_id = self.id_from_uri(obj)
		
		#print '--->  RxNorm check if', subject_id, relation, object_id
		query = """SELECT COUNT(*) FROM RXNREL
			WHERE RXCUI1 = ? AND RXCUI2 = ? AND RELA = ?"""
		
		res = self.sqlite.executeOne(query, (object_id, subject_id, relation))[0]
		return res > 0



# ============================================================================== SNOMED CT
class SNOMED(Lookup):
	""" Handling SNOMED lookups.
	"""
	
	def __init__(self):
		self.sqlite = SQLite.get('databases/snomed.db')
	
	
	def has_relation(self, subj, relation, obj):
		""" Checks the SNOMED relations for our desired triple.
		"""
		
		subject_id = self.id_from_uri(subj)
		object_id = self.id_from_uri(obj)
		
		#print '--->  SNOMED check if', subject_id, relation, object_id
		query = """SELECT COUNT(*) FROM relationships
			WHERE source_id = ? AND destination_id = ? AND rel_text = ?"""
		
		res = self.sqlite.executeOne(query, (subject_id, object_id, relation))[0]
		return res > 0
	
	
	def lookup_term(cls, snomed_id):
		""" Returns the term for the given SNOMED code.
		"""
		if snomed_id is not None:
			sql = 'SELECT term FROM descriptions WHERE concept_id = ?'
			res = self.sqlite.executeOne(sql, (snomed_id,))
			if res:
				return res[0]
		
		return ''

		
		

