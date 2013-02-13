Decision Rule Format
====================

WIP. 


Rule
----

The rule is the host for the conditions and actions, described below. It defines the scope of the rule (currently `record` only) and gives more information about the rule:

* `id` _string_  
  The id of the rule, optimally just an alphanumeric string.
* `scope` _string_  
  The scope to which the rule is applied. Currently only _record_ is implemented, meaning the rule should be checked against one patient.
* `name` _string_  
  A name to show to users.
* `description` _string_  
  A longer description.
* `references` _array_  
  A list of URLs where more information about the rule can be found, or references in general such as publications or FDA statements.

```javascript
{
	"id": "leflunomide",
	"scope": "patient",
	"name": "Leflunomide Hepatotoxicity",
	"description": "Checks for a documented liver failure (SNOMED 59927004) in patients presently or previously on Leflunomide (Arava, RxNorm 27169)",
	"references": [
		"http://www.fda.gov/..."
	]
	"condition": { <condition-set or condition> },
	"actions": [ <action>, <action>, ... ]
}
```


Conditions
----------

Rules can have an arbitrary, nested combination of **AND** or **OR** conditions. This is an outside-in evaluation. For example a condition set that checks whether any medicatin has a given ingredient AND any problem is of a given type:

```javascript
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
```


Actions
-------

TODO.


Why not GELLO/Arden/Lisp/Rumantsch?
-----------------------------------

Not yet decided, I'm still looking into existing CDS languages.
