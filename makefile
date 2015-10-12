.PHONY: db fetch compile all

all: compile
db:
	cat db.sql | psql -d prednavse -U io -W
fetch:
	./fetch.py
compile: fetch
	./compile.py > index.html
