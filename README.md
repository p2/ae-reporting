Adverse Event Reporting
=======================

These aren't the droids you're looking for. You can go about your business.


AppFog
------

This is now an AppFog app, remember to update:

    $ af login
    $ af update ae-reporting


### RxNORM ###

The script `databases/rxnorm.sh` sets up a local SQLite database from a provided RxNORM download.

- download the [latest RxNorm full release](http://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html) and unzip it
- Open that RxNorm_xxx directory
- we're going to create a MySQL database first, so move all files from `rrf` into `scripts/mysql`
- adjust the credentials in the script `scripts/mysql/populate_mysql_rxn.sh`. Use the name _rxnorm_ for the database name so you won't have to adjust our script that loads the SQLite database.
- run the script `scripts/mysql/populate_mysql_rxn.sh`
- if this runs successfully, run our script `databases/rxnorm.sh` (from inside that databases directory). It will use the root MySQL user and dump the database _rxnorm_ into `rxnorm.db`.



### SNOMED CT ###

NOT YET DONE: Setting up SNOMED CT:

- download [SNOMED CT](http://download.nlm.nih.gov/umls/kss/IHTSDO20120731/SnomedCT_Release_INT_20120731.zip)
- Descriptions are in _SnomedCT_Release_INT_20120731/RF2Release/Full/Terminology/sct2_Description_Full-en_INT_20120731.txt_. Those will automatically be imported into a local SQLite database. If you download a different release, update the path in `run.py` to point to the correct file.
