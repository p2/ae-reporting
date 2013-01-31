Decision Rule Format
====================


Rule
----

	{
		"scope": "patient",
		"name": "Leflunomide Hepatotoxicity",
		"description": "Checks for a documented liver failure (SNOMED 59927004) in patients presently or previously on Leflunomide (Arava, RxNorm 27169)",
		"condition": { <condition-set or condition> },
		"actions": [ <action>, <action>, ... ]
	}


Conditions
----------

Rules can have an arbitrary, nested combination of **AND** or **OR** conditions. There is an inside-out evaluation. For example a condition set that checks whether any medicatin has a given ingredient AND any problem is of a given type:

	"type": "all",
	"conditions": [
		{
			"system": "rxnorm",
			"subject": "<http://smartplatforms.org/terms#Medication>",
			"predicate": "has_ingredient",
			"object": "<http://purl.bioontology.org/ontology/RXNORM/27169>"
		},
		{
			"system": "snomed",
			"subject": "<http://smartplatforms.org/terms#Problem>",
			"predicate": "isa",
			"object": "<http://purl.bioontology.org/ontology/SNOMEDCT/59927004>"
		}
	]


Actions
-------