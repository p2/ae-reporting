#!/bin/sh
#
#  create an RxNORM SQLite database

if [ -e rxnorm.db ]; then
	echo "rxnorm.db already exists"
	exit 0
fi

# this is a nice script to import MySQL databases to SQLite, use it
if [ ! -e mysql2sqlite.sh ]; then
	git clone https://gist.github.com/943776.git mysql2sqlite
	mv mysql2sqlite/mysql2sqlite.sh ./
	rm -rf mysql2sqlite
	chmod u+x mysql2sqlite.sh
fi

read -s -p "Enter the MySQL root password: " password
./mysql2sqlite.sh -u root -p$password rxnorm | sqlite3 rxnorm.db

