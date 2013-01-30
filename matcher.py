#!/usr/bin/env python
#
#	2013-01-30	Created by Pascal Pfiffner
#


class Matcher(object):
	""" Abstract superclass to all our rule/condition classes """
	
	def match_against(self, patient):
		""" This method should run the tests against the patient (a TestRecord instance) """
		return False

