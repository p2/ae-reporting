Adverse Event Reporting
=======================

These aren't the droids you're looking for. You can go about your business.

Requirements
------------

Required Python modules:

* bottle
* oauth2
* rdflib
* rdfextras
* jinja2


AppFog
------

This is now an AppFog app, remember to update:

    $ af login
    $ af update ae-reporting


RDF Store
---------

Not currently used in the app, was testing RDF magic with [4store](http://4store.org/), to setup:

    brew install 4store
    4s-backend-setup test
    4s-backend test
    4s-httpd -p 7777 test
    
To import RxNorm:

    cd databases
    ./rxnorm.sh
    4s-import test rxnorm.nt

Adding our test patient's RDF and opening a SPARQL shell

    4s-import test --add ../test.rdf
    4s-query test


UMLS Terminologies
------------------

### RxNORM ###

The script `databases/rxnorm.sh` sets up a local SQLite database from a provided RxNORM download.

- download the [latest RxNorm full release](http://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html) and unzip it
- Open that RxNorm_xxx directory
- we're going to create a MySQL database first, so move all files from `rrf` into `scripts/mysql`
- adjust the credentials in the script `scripts/mysql/populate_mysql_rxn.sh`. Use the name _rxnorm_ for the database name so you won't have to adjust our script that loads the SQLite database.
- run the script `scripts/mysql/populate_mysql_rxn.sh`
- if this runs successfully, run our script `databases/rxnorm.sh` (from inside that databases directory). It will use the root MySQL user and dump the database _rxnorm_ into `rxnorm.db`.



### SNOMED CT ###

Setting up SNOMED CT:

- download [SNOMED CT](http://www.nlm.nih.gov/research/umls/licensedcontent/snomedctfiles.html) and unzip it
- From the directory _SnomedCT_Release_INT_20120731/RF2Release/Full/Terminology_ place the following files under the given name into `databases`:

  - `sct2_Description_Full-en_INT_20120731.txt`: `snomed_desc.csv`
  - `sct2_Relationship_Full_INT_20130131.txt`: `snomed_rel.csv`
  
  This will automatically import all SNOMED codes into a local SQLite database (if not already done).
