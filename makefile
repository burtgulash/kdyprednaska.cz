.PHONY: db fetch compile all css clean

all: css compile
db:
	cat db.sql | psql -d kdyprednaska -U kdyprednaska -W
fetch:
	./fetch.py
compile:
	./compile.py
css:
	mkdir -p dist/css
	sassc s.scss dist/css/style.css
clean:
	if [ -d dist ]; then rm -r dist; fi
	mkdir -p dist
