.PHONY: db fetch compile all css clean res

all: css compile res
db:
	cat db.sql | psql -d kdyprednaska -U kdyprednaska -W
fetch:
	./fetch.py
compile:
	./compile.py
css:
	mkdir -p dist/css
	sassc s.scss dist/css/style.css
res:
	cp -r ./res/* dist
clean:
	if [ -d dist ]; then rm -r dist; fi
	mkdir -p dist
