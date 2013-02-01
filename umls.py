#!/usr/bin/env python
#
#	utilities to handle UMLS
#
#	2013-01-01	Created by Pascal Pfiffner
#


import csv
import sys
import os.path

from sqlite import SQLite


class UMLS (object):
	""" Handling UMLS
	"""
	
	sqlite_handle = None
	umls_file = None
	
	
	@classmethod
	def lookup_snomed(cls, snomed_id):
		""" Returns the term for the given SNOMED code.
		"""
		if not snomed_id:
			raise Exception('No SNOMED code provided')
		
		sql = 'SELECT term FROM descriptions WHERE concept_id = ?'
		res = cls.sqlite_handle.executeOne(sql, (snomed_id,))
		if res:
			return res[0]
		
		return ''
	
	
	@classmethod
	def import_snomed_if_necessary(cls):
		""" Read SNOMED CT from tab-separated file and create an SQLite database
		from it.
		"""
		
		cls.setup_tables()
		
		# need to import descriptions?
		num_query = 'SELECT COUNT(*) FROM descriptions'
		num_existing = UMLS.sqlite_handle.executeOne(num_query, ())[0]
		if num_existing > 0:
			return
		
		snomed_file = 'databases/snomed_desc.csv'
		if not os.path.exists(snomed_file):
			return
		
		cls.import_csv_into_table(snomed_file, 'descriptions')
	
	@classmethod
	def import_csv_into_table(cls, snomed_file, table_name):
		print '..>  Importing SNOMED concepts into snomed.db...'
		
		# not yet imported, parse tab-separated file and import
		with open(snomed_file, 'rb') as csv_handle:
			reader = unicode_csv_reader(csv_handle, dialect='excel-tab')
			i = 0
			try:
				for row in reader:
					if i > 0:
						
						# execute SQL (we just ignore duplicates)
						sql = '''INSERT OR IGNORE INTO %s
							(concept_id, lang, term, active)
							VALUES
							(?, ?, ?, ?)''' % table_name
						params = (int(row[4]), row[5], row[7], row[2])
						try:
							cls.sqlite_handle.execute(sql, params)
						except Exception as e:
							sys.exit(u'Cannot insert %s: %s' % (params, e))
					i += 1
				
				# commit to file
				cls.sqlite_handle.commit()
			
			except csv.Error as e:
				sys.exit('CSV error on line %d: %s' % (reader.line_num, e))

		print '..>  %d concepts parsed' % (i-1)


	@classmethod
	def setup_tables(cls):
		""" Creates the SQLite tables and imports SNOMED from flat files, if
		not already done
		"""
		if cls.sqlite_handle is None:
			cls.sqlite_handle = SQLite.get('databases/snomed.db')
		
		cls.sqlite_handle.create('descriptions', '''(
				concept_id INTEGER PRIMARY KEY,
				lang TEXT,
				term TEXT,
				active INT
			)''')
		

# the standard Python CSV reader can't do unicode, here's the workaround
def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
	csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
	for row in csv_reader:
		yield [unicode(cell, 'utf-8') for cell in row]

