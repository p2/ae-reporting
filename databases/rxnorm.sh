#!/bin/sh
#
#  create an RxNORM SQLite database and a relations triple store.
#  for this to work, the RxNorm distribution needs to live in a local MySQL database named "rxnorm".
#

if [ -e rxnorm.nt ]; then
	exit 0
fi

# need to have an SQLite database first
if [ ! -e rxnorm.db ]; then
	
	# this is a nice script to import MySQL databases to SQLite, use it
	if [ ! -e mysql2sqlite.sh ]; then
		git clone https://gist.github.com/943776.git mysql2sqlite
		mv mysql2sqlite/mysql2sqlite.sh ./
		rm -rf mysql2sqlite
		chmod u+x mysql2sqlite.sh
	fi

	read -s -p "Enter the MySQL root password: " password
	./mysql2sqlite.sh -u root -p$password rxnorm | sqlite3 rxnorm.db
fi

# dump to N-Triples
sqlite3 rxnorm.db <<SQLITE_COMMAND
.headers OFF
.separator ""
.mode list
.out rxnorm.nt
SELECT "<http://purl.bioontology.org/ontology/RXNORM/", RXCUI2, "> <http://purl.bioontology.org/ontology/RXNORM#", RELA, "> <http://purl.bioontology.org/ontology/RXNORM/", RXCUI1, "> ." FROM RXNREL WHERE RELA != '';
SQLITE_COMMAND

