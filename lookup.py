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
			uri = uri[1:] + uri[-1:]
		
		# split and return the last component
		return os.path.split(uri)[1]



# ============================================================================== RxNorm
class RxNorm(Lookup):
	""" Hanling RxNorm lookups.
	"""
	
	def __init__(self):
		self.sqlite = SQLite.get('databases/rxnorm.db')
	
	
	def has_relation(self, subj, relation, obj):
		""" Checks RXNREL table for the desired relation.
		"""
		
		# get the RxNorm ids from subject and object and run the query
		subject_id = self.id_from_uri(subj)
		object_id = self.id_from_uri(obj)
		
		query = """SELECT COUNT(*) FROM RXNREL
			WHERE RXCUI1 = ? AND RXCUI2 = ? AND RELA = ?"""
		
		res = self.sqlite.executeOne(query, (object_id, subject_id, relation))[0]
		return res > 0

