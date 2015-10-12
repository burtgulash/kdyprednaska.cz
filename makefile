.PHONY: db

db:
	cat db.sql | psql -d prednavse -U io -W
