Decision Rule Format
====================


Rule
----


Conditionals
------------

Rules can be nested for an arbitrary combination of **AND** or **OR** conditions. There is an inside-out evaluation.

    "conditions": {
		"all": {
			"rules": [
				{},
				{}
			],
			"conditions": {
				"any": {
					"rules": [
					    {},
					    {},
					    {}
					]
				}
			}
		},
		"any": {}
	}


Actions
-------