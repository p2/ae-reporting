#!/usr/bin/env python
#
#	2013-01-30	Created by Pascal Pfiffner
#


class Matcher(object):
	""" Abstract superclass to all our rule/condition classes """
	
	def match_against(self, patient):
		""" This method should run the tests against the patient (a TestRecord instance).
		
		If a match occurs, should call patient.did_match_item() so the patient object gets a change to store the
		matched items for further processing.
		"""
		return False

