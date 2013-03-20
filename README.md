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

### JSON-LD Serializer

    cd rdflib-jsonld
    sudo python setup.py install


AppFog
------

This is an [AppFog]-ready app (Python/Bottle), the `manifest.yml` and `requirements.txt` files are included.

[appfog]: https://www.appfog.com/


UMLS Terminologies
------------------

The app relies on code lookup against RxNorm and SNOMED. To make those lookups reasonably fast we need to setup a local database for these two terminologies.

### RxNORM ###

The script `databases/rxnorm.sh` sets up a local SQLite database from a provided RxNORM download.

- download the [latest RxNorm full release](http://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html) and unzip it
- run our script `databases/rxnorm.sh` (from inside that databases directory). It will create the database `rxnorm.db`.



### SNOMED CT ###

Setting up SNOMED CT:

- download [SNOMED CT](http://www.nlm.nih.gov/research/umls/licensedcontent/snomedctfiles.html) and unzip it
- From the directory _RF2Release/Full/Terminology_ place the following files under the given name into `databases`:

  - `sct2_Description_Full-en_INT_xxxxxxx.txt`: `snomed_desc.csv`
  - `sct2_Relationship_Full_INT_xxxxxxxx.txt`: `snomed_rel.csv`
  
  When these files are present, the app will automatically import all SNOMED codes into a local SQLite database, if this has not already been done.


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
